<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.h

## Purpose
Declares mlx5 device-memory types, conversion helpers, uverbs definitions, and firmware deallocation helpers shared by the DM implementation and mmap cleanup paths.

## Important APIs, Types, And Functions
- `mlx5_ib_dev_dm_ops` and `mlx5_ib_dm_defs` expose provider ops and uverbs definitions from `dm.c`.
- `struct mlx5_ib_dm` is the base mlx5 device-memory object with embedded `ib_dm`, uAPI type, device address, and size.
- `struct mlx5_ib_dm_op_entry` tracks one MEMIC operation mmap entry, operation address, owning MEMIC object, and operation ID.
- `struct mlx5_ib_dm_memic` extends the base object with MEMIC mmap entry, operation xarray, operation mutex, kref, and originally requested length.
- `struct mlx5_ib_dm_icm` extends the base object with SW ICM object ID.
- `to_mdm()`, `to_memic()`, and `to_icm()` convert RDMA core `ib_dm` pointers to mlx5 private objects.
- `mlx5_ib_alloc_dm()`, `mlx5_ib_dm_mmap_free()`, `mlx5_cmd_dealloc_memic()`, and `mlx5_cmd_dealloc_memic_op()` are cross-file entry points.

## Control Flow
The header itself has no executable control flow. It defines the object layout used by `dm.c` allocation/deallocation and by the driver's mmap-free dispatch.

## State And Persistence
The declared structures describe in-memory state for active device-memory allocations and mmap entries. They persist until RDMA core destroys the `ib_dm` object and associated mmap entries drop their references.

## Dependencies And Integration Points
The header includes `mlx5_ib.h` for RDMA and mlx5 private types. It integrates DM code with RDMA core object allocation, user mmap cleanup, and MR registration.

## Risks And Edge Cases
The conversion helpers assume the caller knows the concrete DM type; using `to_memic()` on SW ICM or `to_icm()` on MEMIC would corrupt interpretation. The kref in `mlx5_ib_dm_memic` means freeing is not identical to handle deallocation, so callers must remove mmap entries and let `mlx5_ib_dm_mmap_free()` finish hardware deallocation.

## Test Signals
Build coverage should confirm structure users match the definitions. Runtime DM tests should exercise all conversion paths indirectly by allocating/deallocating MEMIC and SW ICM objects and by closing mmap entries in different orders.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/mlx5/dm.h -->
