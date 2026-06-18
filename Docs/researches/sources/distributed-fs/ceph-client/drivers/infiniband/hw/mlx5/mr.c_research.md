# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mr.c

## Purpose

`mr.c` implements the mlx5 InfiniBand memory-region and memory-window lifecycle. It translates RDMA core requests for DMA MRs, user MRs, ODP MRs, dmabuf MRs, device-memory MRs, memory windows, and integrity/signature MRs into mlx5 MKey creation, update, revocation, and destruction operations. It is also the main owner of SG-to-descriptor mapping for kernel fast-registration MRs and the bridge into UMR-based page-table programming implemented in `umr.c`.

The file sits on the critical data path for RDMA memory access correctness: it decides access flags, page sizes, MKey access mode, whether a translation can be populated directly at create time, whether cached FRMR pool MKeys can be reused, and how to revoke or destroy keys while ODP page faults, dmabuf invalidation, and Data Direct teardown may still race.

## Important APIs, Types, and Functions

Primary exported/provider callbacks:

- `mlx5_ib_get_dma_mr()` creates a physical-address DMA MR with local/remote access bits and optional ATS translation mode.
- `mlx5_ib_reg_user_mr()` registers normal and ODP user memory. It initializes UMR resources, obtains `ib_umem`, and dispatches to `create_real_mr()` or `create_user_odp_mr()`.
- `mlx5_ib_reg_user_mr_dmabuf()` registers dmabuf-backed user memory, including optional mlx5 Data Direct mode via `MLX5_IB_UAPI_REG_DMABUF_ACCESS_DATA_DIRECT`.
- `mlx5_ib_rereg_user_mr()` handles reregistration fast paths for PD/access/PAS changes and recreates the MR when state cannot be preserved.
- `mlx5_ib_dereg_mr()` and `__mlx5_ib_dereg_mr()` revoke, destroy, unmap, and free MRs.
- `mlx5_ib_alloc_mr()`, `mlx5_ib_alloc_mr_integrity()`, `mlx5_ib_map_mr_sg()`, and `mlx5_ib_map_mr_sg_pi()` implement kernel MR allocation and scatterlist descriptor population.
- `mlx5_ib_alloc_mw()` and `mlx5_ib_dealloc_mw()` create and destroy type 1/type 2 memory windows.
- `mlx5_ib_check_mr_status()` exposes signature error status for integrity MRs.
- `mlx5_ib_advise_mr()` validates advice opcodes and forwards prefetch requests to ODP code.

Key helper groups:

- MKey creation: `assign_mkey_variant()`, `mlx5_ib_create_mkey()`, `destroy_mkey()`, `set_mkc_access_pd_addr_fields()`, `get_mkc_octo_size()`.
- FRMR pool integration: `_mlx5_frmr_pool_alloc()`, `mlx5_mr_cache_alloc()`, `mlx5r_create_mkeys()`, `mlx5r_destroy_mkeys()`, `mlx5r_build_frmr_key()`, `mlx5r_frmr_pools_init()`.
- User MR creation: `alloc_cacheable_mr()`, `reg_create()`, `create_real_mr()`, `create_user_odp_mr()`.
- dmabuf/Data Direct: `mlx5_ib_dmabuf_invalidate_cb()`, `reg_user_mr_dmabuf()`, `reg_user_mr_dmabuf_by_data_direct()`, `reg_create_crossing_vhca_mr()`, `mlx5_ib_revoke_data_direct_mrs()`.
- Reregistration: `can_use_umr_rereg_access()`, `can_use_umr_rereg_pas()`, `umr_rereg_pas()`.
- Integrity/PI: `mlx5_alloc_integrity_descs()`, `mlx5_ib_alloc_pi_mr()`, `mlx5_ib_map_pa_mr_sg_pi()`, `mlx5_ib_map_mtt_mr_sg_pi()`, `mlx5_ib_map_klm_mr_sg_pi()`.

The central type is `struct mlx5_ib_mr` from `mlx5_ib.h`. For user MRs it stores `umem`, `page_shift`, `access_flags`, ODP child tracking, dmabuf/Data Direct flags, and a possible null MKey. For kernel MRs it stores DMA-mapped descriptor buffers and integrity sub-MRs. The companion `struct mlx5_ib_mkey` is the hardware identity tracked by the ODP xarray when page faults can reference it.

## Control Flow

Normal user MR registration starts in `mlx5_ib_reg_user_mr()`. The function rejects unsupported configurations, initializes UMR resources, and dispatches ODP requests to `create_user_odp_mr()`. Non-ODP requests obtain an `ib_umem` and call `create_real_mr()`. `create_real_mr()` chooses between a cacheable UMR path and a slow create-with-populated-PAS path. If the memory can be loaded through UMR, it obtains a free cached MKey from the FRMR pool and enables/populates it with `mlx5r_umr_update_mr_pas()`. Otherwise it serializes on `dev->slow_path_mutex`, calls `reg_create()` with `populate=true`, and creates the MKey with the PAS array embedded in the create command.

ODP user MR registration validates that ODP support is compiled and that an ODP page-fault EQ exists. A full address-space implicit ODP MR calls into `mlx5_ib_alloc_implicit_mr()` in `odp.c`; explicit ODP MRs require UMR-loadable length, allocate `ib_umem_odp`, create a cacheable MTT MKey, initialize `implicit_children`, store the MKey in `dev->odp_mkeys`, and prime translations through `mlx5_ib_init_odp_mr()`.

dmabuf registration follows the same cacheable-MKey model but obtains an `ib_umem_dmabuf`. Non-pinned dmabufs register an invalidation callback that zaps translations and unmaps pages under the dma-resv lock. Pinned Data Direct dmabufs use KSM access mode and may create a pair of MRs: a crossed Data Direct MKey and a crossing VHCA MKey visible to the requesting PD.

Reregistration first tries narrow UMR reconfiguration. If only PD or access changes are requested and `mlx5r_umr_can_reconfig()` allows the flag transition, the existing MKey is updated in place. For translation changes, the code obtains a new `ib_umem`, verifies the old FRMR pool allocation has enough descriptor capacity, revokes the old MKey, swaps MR fields, updates PAS through UMR, and releases the old `umem`. Unsupported, ODP, dmabuf, device-memory, Data Direct, or TPH-tagged cases fall back to MR recreation.

Deregistration removes the MKey from `dev->odp_mkeys` when needed, waits for outstanding page-fault users, recursively deregisters integrity sub-MRs, destroys PSVs, revokes or destroys the MKey, releases `umem`, frees ODP child state, unmaps private descriptor buffers, and frees the MR. Data Direct crossing MRs are special: the visible crossing MR is destroyed first, then the crossed MR is removed from `data_direct_mr_list` unless it was already revoked.

Kernel MR allocation creates a free UMR-enabled MKey plus a DMA-mapped descriptor array. SG mapping fills either KLM descriptors or MTT pages and synchronizes the descriptor DMA buffer for device access. Integrity MR mapping tries direct PA descriptors first, then MTT, then KLM fallback, and records which PI sub-MR should be used by send-path code.

## State and Persistence Behavior

Persistent driver state is in kernel memory and hardware MKey tables, not on disk. `dev->mkey_var` generates variant bytes for MKeys; `dev->odp_mkeys` maps base MKeys to live ODP-capable `mlx5_ib_mkey` objects; `dev->sig_mrs` maps signature MKeys to signature contexts; `dev->data_direct_mr_list` tracks pinned crossed Data Direct MRs for reset/revoke flows; FRMR pools retain reusable free MKeys across MR lifetimes.

The code maintains accounting with `dev->mdev->priv.reg_pages`, incrementing on successful user/dmabuf registrations and decrementing when non-ODP `umem` is released. ODP references use `mmkey.usecount` and `mlx5r_deref_wait_odp_mkey()` so asynchronous page-fault or prefetch workers cannot touch a freed MKey.

Hardware state transitions are explicit: MKeys are created free or populated, enabled through UMR updates, revoked before destructive reuse, and destroyed only after they are no longer discoverable by page-fault lookup. dmabuf page tables are invalidated through callback-driven zap and unmap.

## Dependencies and Integration Points

This file depends on RDMA core memory APIs (`ib_umem_get`, `ib_umem_odp_get`, `ib_umem_dmabuf_get`, `ib_sg_to_pages`, uverbs helpers), mlx5 core MKey/PSV commands, UMR helpers in `umr.c`, ODP helpers in `odp.c`, Data Direct helpers, dma-buf reservation locking, and device capability macros from mlx5 IFC headers.

It is wired into the device ops table in `main.c` through `.reg_user_mr`, `.reg_user_mr_dmabuf`, `.rereg_user_mr`, `.alloc_mw`, and `.dealloc_mw`. `wr.c` consumes the mapped integrity MR state when posting signature work requests. `cq.c` consults `dev->sig_mrs` for signature completions. `odp.c` consumes `mlx5_mr_cache_alloc()`, MKey xarray entries, and `mlx5_ib_init_odp_mr()`/`mlx5_ib_init_dmabuf_mr()` flows.

## Risks and Edge Cases

The highest risk areas are lifetime and concurrency around ODP, dmabuf, and Data Direct. MKeys must be removed from xarrays before destruction, and code paths must wait for outstanding page fault users. dmabuf invalidation must hold the dma-resv lock and must not leave `umem_dmabuf->private` pointing to a destroyed MR. Data Direct teardown spans two MRs and a device list protected by `data_direct_lock`.

Fast reregistration is sensitive to descriptor capacity, access-flag immutability, and page-size selection. A bad decision could reuse an MKey with insufficient translation space or expose stale access permissions. Integrity MR setup has multi-resource unwind paths involving PSVs and nested MRs; missing cleanup would leak hardware state or leave stale `sig_mrs` entries.

Other edge cases include relaxed-ordering capability differences, ATS enablement, huge/unaligned dmabuf IOVA, TPH steering fields encoded through FRMR vendor keys, and PAGE/PAS alignment requirements for KSM/Data Direct access mode.

## Test Signals

Useful test signals include RDMA core MR registration/reregistration/deregistration tests, ODP page fault and `IB_UVERBS_ADVISE_MR` prefetch tests, dmabuf invalidation and pinned dmabuf registration tests, memory-window bind/invalidation tests, and integrity/signature error injection. Kernel dynamic checks should watch for `WARN_ON()` in MKey destruction, refcount leaks in `odp_mkeys`, non-empty `sig_mrs`/`odp_mkeys` at device cleanup, reg_pages accounting mismatches, UMR update failures, and dma mapping errors. Data Direct coverage should verify revoke-on-device-removal and crossing/crossed MR deregistration ordering.
