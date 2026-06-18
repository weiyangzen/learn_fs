# Research: subset-b-003945

Grouped research for mlx5 InfiniBand memory registration, ODP fault handling, and packet pacing QoS uAPI files. Each section is delimited for reconciliation into the source-tree-aligned per-file report path.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/odp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/odp.c

## Purpose

`odp.c` implements mlx5 On-Demand Paging support for InfiniBand memory. It populates and invalidates hardware translation tables for ODP MRs, handles explicit, implicit, dmabuf, WQE, RDMA, and memory-scheme page faults, manages the page-fault event queue, advertises ODP capabilities, and implements `advise_mr` prefetch behavior.

The file coordinates three subsystems that must agree under concurrency: Linux MMU interval notifiers and HMM DMA mapping, mlx5 UMR translation-table updates, and asynchronous hardware page-fault events. It also supports implicit ODP by building a two-level translation scheme: a top-level KSM implicit MR points to child MTT MRs that cover large chunks of process address space.

## Important APIs, Types, and Functions

Primary entry points:

- `mlx5_odp_populate_xlt()` fills either MTT entries or KSM entries during UMR updates.
- `mlx5_ib_alloc_implicit_mr()` creates a full-address-space implicit ODP MR.
- `mlx5_ib_free_odp_mr()` releases implicit child MRs and private null MKeys.
- `mlx5_ib_init_odp_mr()` snapshots/prefaults an explicit ODP MR during registration.
- `mlx5_ib_init_dmabuf_mr()` maps and enables dmabuf translations.
- `mlx5r_odp_create_eq()` lazily creates the page-fault EQ, workqueue, notifier, and mempool.
- `mlx5_ib_odp_init_one()`, `mlx5_ib_odp_cleanup_one()`, and `mlx5_ib_odp_init()` initialize device and global ODP state.
- `mlx5_ib_advise_mr_prefetch()` implements synchronous or asynchronous `advise_mr` prefetch.

Important internal types and helpers:

- `struct mlx5_pagefault` normalizes RDMA, WQE, and memory page-fault EQE payloads.
- `populate_mtt()` maps valid HMM PFNs to DMA addresses and builds MTT entries.
- `populate_ksm()` builds implicit KSM entries pointing at child MRs or null MKeys.
- `mlx5_ib_invalidate_range()` is the MMU interval notifier invalidation callback.
- `implicit_get_child_mr()`, `destroy_unused_implicit_child_mr()`, and `free_implicit_child_mr_work()` manage implicit child MR creation and deferred destruction.
- `pagefault_real_mr()`, `pagefault_implicit_mr()`, `pagefault_dmabuf_mr()`, and `pagefault_mr()` map pages and issue UMR translation updates.
- `find_odp_mkey()` resolves fault MKeys from `dev->odp_mkeys` with reference protection.
- `pagefault_single_data_segment()` walks direct and indirect MKeys for a data segment.
- `mlx5_ib_mr_wqe_pfault_handler()`, `mlx5_ib_mr_rdma_pfault_handler()`, and `mlx5_ib_mr_memory_pfault_handler()` resolve the three page-fault subtypes.

## Control Flow

During initialization, `mlx5_ib_odp_init()` derives implicit MR geometry from `TASK_SIZE`: child MTT coverage is 1 GiB for common 48-bit address spaces or 16 GiB for 56-bit address spaces. `mlx5_ib_odp_init_one()` fills ODP capabilities from hardware support for page-granular access, UMR, transport-specific ODP operations, null MKeys, fixed buffer size, and indirect MKeys. The page-fault EQ is created lazily by MR registration through `mlx5r_odp_create_eq()`.

ODP translation updates call `mlx5_odp_populate_xlt()`. MTT population skips zap operations, maps valid HMM PFNs through `hmm_dma_map_pfn()`, sets read/write bits, and increments `odp->npages`. KSM population for implicit ODP installs child MR lkeys when present and null MKeys otherwise. The KSM update path requires `umem_mutex` to pair xarray changes with hardware translation updates.

Invalidation starts from `mlx5_ib_invalidate_range()`. The callback refuses non-blockable ranges, locks `umem_mutex`, updates the interval sequence, scans valid PFNs overlapping the invalidation range, zaps aligned blocks of MTT entries with atomic UMR updates, updates ODP invalidation stats, unmaps DMA pages, and schedules destruction of now-empty implicit child MRs.

Page-fault handling begins in the EQ interrupt notifier. `mlx5_ib_eq_pf_process()` drains EQEs, allocates `mlx5_pagefault` objects from a mempool, decodes subtype-specific fields, and queues work on a high-priority workqueue. Worker code dispatches to WQE, RDMA, or memory-scheme handlers and always resumes the hardware fault with success or error unless the event protocol says only the last memory-fault fragment should resume.

WQE faults hold the QP/SRQ resource, copy the relevant WQE, parse transport-specific headers to find data segments, and call `pagefault_data_segments()`. RDMA faults map the rkey/address range needed for forward progress, resume the QP, then optionally prefetch more. Memory-scheme faults resolve the MKey directly, map a prefetch window if possible, fall back to the demanded range, and resumes only on `MLX5_MEMORY_PAGE_FAULT_FLAGS_LAST`.

`pagefault_single_data_segment()` handles direct ODP MRs and indirect MKeys/MWs. Direct MRs are mapped by `pagefault_mr()`. Indirect keys are queried with `mlx5_core_query_mkey()`, converted into stack-like frames of KLM segments, and followed recursively up to the device `max_indirection` limit. Non-ODP MKeys are treated as already resident so mixed SGLs can progress.

Prefetch through `mlx5_ib_advise_mr_prefetch()` validates each lkey against the caller PD, checks write-prefetch permissions, then either maps synchronously when `IB_UVERBS_ADVISE_MR_FLAG_FLUSH` is set or queues async work that holds ODP MKey references until complete.

## State and Persistence Behavior

State is runtime-only. Global static geometry (`mlx5_imr_mtt_entries`, `mlx5_imr_ksm_entries`, page shifts, and MTT size) is computed once from virtual address width. Per-device state includes `dev->odp_caps`, `dev->odp_max_size`, `dev->odp_eq_mutex`, `dev->odp_pf_eq`, and `dev->odp_mkeys`.

Per-MR state lives in `mlx5_ib_mr`: ODP MRs store `umem`, `page_shift`, stats, implicit-child xarray, parent pointers, and optional null MKey. `ib_umem_odp` stores HMM PFN state, DMA mapping state, `npages`, notifier state, and a private backpointer to the MR. Reference counts on `mlx5_ib_mkey` protect objects while page-fault and prefetch workers are active.

Hardware state changes are translation-table updates: zap, enable, downgrade, indirect KSM updates, dmabuf page-size updates, and page-fault resume commands. The file treats MMU invalidation and page-fault repair as a synchronization protocol, using `umem_mutex`, dma-resv locks, xarray locks, and deferred work to avoid sleeping in invalidation-critical sections.

## Dependencies and Integration Points

`odp.c` depends on RDMA ODP core (`ib_umem_odp_*`), MMU interval notifiers, HMM and HMM DMA mapping, dma-buf reservation locks, pci p2pdma mapping state, mlx5 EQ APIs, mlx5 core resource holding for QPs/SRQs, WQE readers in `qp.c`, MKey creation and deregistration in `mr.c`, and UMR update APIs in `umr.c`.

It is integrated with `mr.c` registration paths: explicit ODP and dmabuf MRs are initialized here; implicit ODP MRs are allocated here; MKeys created in `mr.c` are stored in `dev->odp_mkeys` for lookup here. `main.c` uses `mlx5_ib_odp_init_one()` to advertise `.advise_mr` and cleanup destroys the ODP EQ.

## Risks and Edge Cases

Concurrency is the dominant risk. MMU invalidation can race with page faults, implicit child MR creation, child destruction, and MR deregistration. The code relies on strict ordering around xarray store/erase, `umem_mutex`, MKey refcounts, and hardware UMR updates. A missed reference or out-of-order KSM update can cause use-after-free or repeated hardware faults.

Fault handlers must resume hardware correctly. Returning success before enough bytes are mapped can corrupt forward progress, while failing to resume can stall a QP. RDMA faults with unknown length depend on packet-size prefetch heuristics. Memory-scheme faults have token and "last fragment" semantics that differ from transport faults.

Other edge cases include invalid virtual ranges, zero-length WQE segments meaning 2 GiB, nested indirect MKeys beyond `max_indirection`, non-ODP lkeys in mixed SGLs, dma-buf page-size changes after first fault, HMM PFNs without write access, p2pdma mapping failures, and implicit address-space geometry on architectures outside the handled VA sizes.

## Test Signals

High-value tests include ODP explicit MR page faults for read/write/atomic operations, implicit ODP over sparse address ranges, concurrent munmap/mprotect invalidation during RDMA traffic, nested MW/indirect MKey page faults, dmabuf page faults and invalidations, `advise_mr` prefetch with and without flush, and device cleanup while faults are outstanding. Runtime signals include ODP fault/prefetch/invalidation counters, page-fault resume errors, `-EAGAIN` retry paths, mempool/workqueue exhaustion, non-empty `odp_mkeys` at cleanup, and lockdep coverage for `umem_mutex` and dma-resv ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/odp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qos.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qos.c

## Purpose

`qos.c` exposes mlx5 packet pacing rate-limit objects through the RDMA uverbs named-ioctl API. It lets DEVX-capable userspace allocate a packet pacing object, receive a hardware rate-limit table index, and later destroy that object. QPs can then use the returned index when configuring packet pacing.

The file is intentionally small: it provides capability gating, one allocation handler, one cleanup handler, uverbs object/method declarations, and the `mlx5_ib_qos_defs` uAPI definition chain consumed by mlx5 device setup.

## Important APIs, Types, and Functions

- `pp_is_supported()` gates the uAPI object on general QoS support, packet pacing support, and packet pacing UID support.
- `UVERBS_HANDLER(MLX5_IB_METHOD_PP_OBJ_ALLOC)` handles object allocation. It obtains the caller ucontext, requires `devx_uid`, copies the raw mlx5 rate-limit context, parses allocation flags, chooses either the caller DEVX UID or shared resource UID, calls `mlx5_rl_add_rate_raw()`, finalizes the uobject, and returns the allocated index.
- `pp_obj_cleanup()` removes the raw rate with `mlx5_rl_remove_rate_raw()` and frees the `struct mlx5_ib_pp` object.
- `DECLARE_UVERBS_NAMED_METHOD`, `DECLARE_UVERBS_NAMED_METHOD_DESTROY`, and `DECLARE_UVERBS_NAMED_OBJECT` define the object ABI around `MLX5_IB_OBJECT_PP`.
- `mlx5_ib_qos_defs[]` chains the object tree into the mlx5 uAPI only when `pp_is_supported()` returns true.

The main persistent kernel object is `struct mlx5_ib_pp`, which stores the mlx5 core device pointer and the allocated rate-limit index. The userspace ABI identifiers come from `rdma/mlx5_user_ioctl_cmds.h` and `rdma/mlx5_user_ioctl_verbs.h`.

## Control Flow

Allocation begins when userspace calls the named uverbs method `MLX5_IB_METHOD_PP_OBJ_ALLOC`. The handler resolves the `MLX5_IB_ATTR_PP_OBJ_ALLOC_HANDLE` uobject and the mlx5 ucontext. Non-DEVX contexts are rejected because the allocated entry can be used only by DEVX flows. The handler allocates `struct mlx5_ib_pp`, copies the bounded raw `set_pp_rate_limit_context` input into a fixed-size buffer, parses `MLX5_IB_UAPI_PP_ALLOC_FLAGS_DEDICATED_INDEX`, and chooses a UID. A dedicated index uses the calling context's `devx_uid`; otherwise the shared resource UID is used.

`mlx5_rl_add_rate_raw()` programs or reserves the rate-limit entry and returns the hardware index. On success, the object stores `mdev` and index, assigns `uobj->object`, finalizes creation, and copies the index to the mandatory output attribute. Destroying the uobject invokes `pp_obj_cleanup()`, which removes the raw rate by index and frees the allocation.

## State and Persistence Behavior

State is runtime-only. Each uverbs PP object owns one `struct mlx5_ib_pp` and one hardware rate-limit index. Lifetime is tied to the uobject IDR entry: finalize publishes the object to userspace, and destroy or ucontext cleanup calls the cleanup callback. No file-backed or persistent state is written.

The hardware rate-limit table is external state managed by mlx5 core rate-limit helpers. The cleanup path assumes `pp_entry->index` was successfully allocated before object publication; allocation failures before publication free memory locally and do not install a cleanup-visible object.

## Dependencies and Integration Points

The file depends on RDMA uverbs named-ioctl infrastructure, mlx5 user ioctl ABI headers, mlx5 capability macros, mlx5 core rate-limit helpers, and the mlx5 ucontext DEVX UID. `main.c` chains `mlx5_ib_qos_defs` into the device uAPI tree. Query-device code advertises packet pacing caps, and QP modification code uses packet pacing rate-limit indices in SQ context fields.

## Risks and Edge Cases

The input context is copied into a fixed-size stack buffer after uverbs enforces an attribute size range from 1 byte to `MLX5_ST_SZ_BYTES(set_pp_rate_limit_context)`. Correctness depends on uverbs validation and mlx5 core parsing of partially supplied raw contexts. A failure after `uverbs_finalize_uobj_create()` but before copying the index to userspace would leave a live object even though the method returns an error; callers must handle ordinary uverbs semantics for finalized objects, and this path is worth testing.

Capability gating must stay aligned with hardware requirements. Exposing the object without packet pacing UID support would allow contexts to allocate entries they cannot safely own. Cleanup assumes `uobject->object` is valid and initialized, which is true only for finalized allocations.

## Test Signals

Test with devices that both support and do not support QoS packet pacing UID capabilities. Exercise allocation with shared and dedicated flags, invalid flags, non-DEVX contexts, short and full-size raw contexts, allocation failure injection in `mlx5_rl_add_rate_raw()`, destroy after successful allocation, and ucontext teardown with live PP objects. Integration tests should verify a QP can consume the returned index and that rate entries are removed after object destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/qos.c -->
