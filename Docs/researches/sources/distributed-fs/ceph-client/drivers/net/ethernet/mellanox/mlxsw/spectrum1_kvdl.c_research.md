# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum1_kvdl.c

## Purpose

`spectrum1_kvdl.c` implements the Spectrum-1 KVD linear allocator. Spectrum-1 divides the linear KVD space into three fixed-granularity partitions: single entries, 32-entry chunks, and 512-entry large chunks. The file allocates and frees entries from bitmap-backed partitions, reports devlink resource occupancy, and registers Spectrum-1-specific devlink resources for the KVD linear sub-partitions.

## Important APIs, Types, and Functions

The exported operation table is `mlxsw_sp1_kvdl_ops`, with `init`, `fini`, `alloc`, `free`, and `alloc_size_query` callbacks. `mlxsw_sp1_kvdl_resources_register()` registers the devlink child resources for singles, chunks, and large chunks.

`struct mlxsw_sp1_kvdl_part_info` describes a partition's start/end index, allocation size, and devlink resource ID. `struct mlxsw_sp1_kvdl_part` stores a mutable copy of that info plus a flexible bitmap. `struct mlxsw_sp1_kvdl` stores the three partition pointers.

Allocation helpers select the smallest partition whose allocation size can hold the requested entry count, find the first zero usage bit, set it, and translate the bit index to a KVDL index. Freeing finds the owning partition by index and clears the corresponding usage bit.

## Control Flow

Initialization builds each partition in order. For each partition it tries to read an overridden devlink resource size. If a size is present, it updates that partition's start/end so partitions are packed consecutively according to configured sizes; otherwise it uses compile-time defaults. It allocates a usage bitmap sized by `resource_size / alloc_size`. After all parts are initialized, it registers occupancy callbacks for the aggregate linear resource and each child partition.

Allocation ignores entry type and is size-driven. `alloc_size_query` returns the selected partition allocation size so higher-level code can know how many entries a request consumes. Finalization unregisters occupancy callbacks in reverse order and frees all partitions.

## State and Persistence Behavior

Persistent state is in-memory usage bitmaps per partition. Occupancy is derived by scanning set bits and multiplying by partition allocation size. Hardware cleanup is not issued in this file when freeing; Spectrum-1 callers are responsible for overwriting or invalidating the hardware records they used.

Devlink resource sizes can affect partition boundaries at initialization. Those choices persist for the device lifetime but are not stored by this file.

## Dependencies and Integration Points

The allocator is selected through `mlxsw_sp->kvdl_ops` for Spectrum-1. It depends on `spectrum.h` constants and devlink resource APIs. Its allocations back ACL action sets, adjacency data, multicast/NVE structures, IPv6 addresses, and other KVDL users through the generic `mlxsw_sp_kvdl_*()` wrappers.

## Risks and Edge Cases

- Allocation is first-fit and always chooses the smallest sufficient allocation size. Long-running mixed workloads can fragment each fixed partition independently.
- `free()` silently returns if the index does not belong to a known partition, which prevents a crash but can hide double-free or corrupted-index bugs.
- The allocator does not use the entry type, so type-specific isolation is not enforced on Spectrum-1.
- Resource override sizes are packed sequentially; invalid or surprising devlink sizing can shift later partition ranges.
- Bitmap updates are not locally locked. Correctness depends on serialization in upper KVDL users or driver control paths.

## Test Signals

Validate devlink resource registration and occupancy for all three partitions, allocation-size queries for requests of 1, 32, 512, and oversized counts, exhaustion behavior, free/reallocate reuse, devlink size override boot paths, and stress with mixed ACL/action/NVE/router users.
