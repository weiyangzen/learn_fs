<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.c

## Purpose
Implements mlx5 device memory (`ib_dm`) support for MEMIC device memory and software-owned ICM allocations. It provides uverbs allocation/query/mmap metadata, MEMIC operation-address mapping, and provider `alloc_dm`, `dealloc_dm`, and `reg_dm_mr` hooks.

## Important APIs, Types, And Functions
- MEMIC firmware commands: `mlx5_cmd_alloc_memic()`, `mlx5_cmd_dealloc_memic()`, `mlx5_cmd_alloc_memic_op()`, and `mlx5_cmd_dealloc_memic_op()` allocate/free MEMIC ranges and operation addresses through mlx5 firmware.
- mmap setup: `add_dm_mmap_entry()` inserts RDMA user mmap entries for device memory and MEMIC operation windows.
- MEMIC lifetime: `handle_alloc_dm_memic()`, `mlx5_dm_memic_dealloc()`, `dm_memic_remove_ops()`, `mlx5_ib_dm_memic_free()`, and `mlx5_ib_dm_mmap_free()` manage MEMIC allocation, mmap references, operation mappings, and final hardware deallocation.
- MEMIC op uAPI: `MLX5_IB_METHOD_DM_MAP_OP_ADDR`, `map_existing_op()`, `copy_op_to_user()`, and `mlx5_cmd_alloc_memic_op()` expose operation-specific addresses when firmware supports the requested operation bit.
- SW ICM lifetime: `get_icm_type()`, `handle_alloc_dm_sw_icm()`, and `mlx5_dm_icm_dealloc()` allocate/free software ICM for steering, header modify, modify-header pattern, and encap use cases.
- Public provider entry: `mlx5_ib_alloc_dm()` selects MEMIC or SW ICM by optional uAPI type.
- Query/uAPI registration: `MLX5_IB_METHOD_DM_QUERY`, `mlx5_ib_dm_defs`, and `mlx5_ib_dev_dm_ops` register query, map-op, allocation attributes, and device ops.

## Control Flow
MEMIC allocation validates length and alignment, scans `dev->dm.memic_alloc_pages` under `dm->lock` for a free aligned range, tentatively marks pages busy, then issues `ALLOC_MEMIC`. If firmware returns `-EAGAIN`, the range is unmarked and the scan advances; other errors fail; success returns a BAR-relative physical address adjusted by `dev->bar_addr`. `handle_alloc_dm_memic()` rounds the requested length to MEMIC granularity, allocates a `mlx5_ib_dm_memic`, initializes refcount/xarray/mutex state, allocates MEMIC hardware memory, inserts a user mmap entry, and returns page index/start offset to userspace.

`MLX5_IB_METHOD_DM_MAP_OP_ADDR` validates the requested operation index, checks the firmware operation bitmap, returns an existing mapping if present, or allocates a new operation address. It inserts a separate mmap entry, takes a MEMIC reference before exposing the entry, copies page index/offset to userspace, and stores the op entry in `dm->ops`. Cleanup removes mmap entries first; final hardware MEMIC deallocation occurs only when all mmap references and operation entries drop the MEMIC kref.

SW ICM allocation is capability and privilege gated. It requires both `CAP_SYS_RAWIO` and `CAP_NET_RAW`, validates the requested DM type against `sw_owner`/`sw_owner_v2` capabilities, rounds allocation size to a power-of-two multiple of the device block size, calls `mlx5_dm_sw_icm_alloc()` with the user context DEVX UID, and returns the device address as the start offset.

## State And Persistence
State includes MEMIC allocation bitmap pages in `struct mlx5_dm`, MEMIC device addresses and sizes in `struct mlx5_ib_dm`, per-MEMIC operation xarray, mmap entries stored in RDMA core, krefs that couple mmap lifetime to hardware deallocation, and SW ICM object IDs/device addresses. All state is in-memory plus firmware/BAR allocations; no filesystem persistence exists.

## Dependencies And Integration Points
The file depends on RDMA uverbs named-ioctl, RDMA user mmap entries, mlx5 device-memory firmware capabilities/commands, xarray, kref, Linux capability checks, and `mlx5_ib_reg_dm_mr()` supplied elsewhere. It integrates with the driver's mmap-free path through `mlx5_ib_dm_mmap_free()` and with DEVX/user contexts through SW ICM allocation using `to_mucontext(ctx)->devx_uid`.

## Risks And Edge Cases
MEMIC allocation must keep the bitmap synchronized with firmware allocation/deallocation; `mlx5_cmd_dealloc_memic()` clears the bitmap only after firmware deallocation succeeds, which avoids reuse after failed free but can strand bitmap space if firmware returns an error. `MLX5_IB_METHOD_DM_MAP_OP_ADDR` allocates `op_entry` but on allocation failure after `kzalloc_obj()` the local `err` value must already be meaningful; reviewers should check that path. MEMIC kref/mmap ordering is delicate because user mmap entries can outlive the `ib_dm` handle. SW ICM exposes privileged steering memory and therefore depends on capability and firmware feature gating.

## Test Signals
Run uverbs DM allocation/query/mmap tests for MEMIC, MEMIC operation mapping, and all SW ICM types. Include invalid length/alignment, unsupported operation bits, repeated map-op returning existing entries, mmap close before/after DM dealloc, firmware `-EAGAIN` allocation retry, SW ICM privilege denial, capability-denied paths, DM-backed MR registration, and leak/KASAN checks for mmap and xarray cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.c -->
