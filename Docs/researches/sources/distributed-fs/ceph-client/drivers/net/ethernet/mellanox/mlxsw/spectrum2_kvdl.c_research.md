# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum2_kvdl.c

## Purpose

`spectrum2_kvdl.c` implements the Spectrum-2-and-newer KVD linear allocator. Unlike Spectrum-1's fixed size classes, Spectrum-2 partitions KVDL by entry type and sizes those partitions from firmware resources. It tracks usage with bitmaps, allocates contiguous groups of usage bits for variable entry counts, asks firmware to delete freed KVDL records, and exposes generic KVDL operations.

## Important APIs, Types, and Functions

The exported operation table is `mlxsw_sp2_kvdl_ops`. `struct mlxsw_sp2_kvdl_part_info` maps each `enum mlxsw_sp_kvdl_entry_type` to a firmware IEDR resource type plus resource IDs used to determine usage bit count and index range. Supported parts include `ADJ`, `ACTSET`, `PBS`, `MCRIGR`, `IPV6_ADDRESS`, and `TNUMT`.

`struct mlxsw_sp2_kvdl_part` stores part info, usage bit count, indexes per usage bit, last allocated bit, and a flexible usage bitmap. Allocation uses `mlxsw_sp2_kvdl_part_find_zero_bits()` and `mlxsw_sp2_kvdl_part_alloc()`. Freeing uses `mlxsw_sp2_kvdl_rec_del()` to issue an `IEDR` delete record before clearing bitmap bits.

## Control Flow

Initialization iterates over the part-info array. For each entry type it requires both resource IDs, reads `usage_bit_count` and `index_range`, computes `indexes_per_usage_bit = index_range / usage_bit_count`, allocates the usage bitmap, and initializes `last_allocated_bit` to the last bit so the first allocation starts from zero.

Allocation converts entry count to hardware index size with `entry_count * mlxsw_sp_kvdl_entry_size(type)`, finds a contiguous free run of enough usage bits with wrap-around search, sets those bits, and returns `bit * indexes_per_usage_bit` as the KVDL index. Freeing computes the same size, writes an IEDR delete record for the resource type, and only clears bitmap bits if firmware deletion succeeds. `alloc_size_query` returns the requested entry count unchanged.

## State and Persistence Behavior

In-memory state is per-entry-type usage bitmaps and the `last_allocated_bit` cursor. Allocation is type-isolated: each entry type has a separate partition and firmware resource type. Hardware state is explicitly touched on free through `IEDR`, so the allocator coordinates both software reuse and firmware record invalidation.

There are no devlink occupancy callbacks in this file, unlike the Spectrum-1 allocator. Capacity comes from firmware resources queried during core resource discovery.

## Dependencies and Integration Points

The allocator is selected by Spectrum-2, Spectrum-3, and Spectrum-4 init paths. It depends on `resources.h` resource IDs, mlxsw core resource accessors, `IEDR` register helpers, and generic `mlxsw_sp_kvdl_*()` wrappers. It backs ACL action sets, adjacencies, port-buffer structures, multicast records, IPv6 address records, and tunnel/NVE tables depending on entry type.

## Risks and Edge Cases

- `indexes_per_usage_bit` is computed with integer division and is not checked for zero or remainder. Bad firmware resources could cause division-by-zero-adjacent behavior or under-accounted capacity.
- `mlxsw_sp2_kvdl_part_find_zero_bits()` uses `bit + bit_count >= usage_bit_count` as an end test, so exact-fit-at-end behavior should be reviewed carefully for off-by-one capacity loss.
- `last_allocated_bit` is never updated after successful allocation in this implementation, so allocation starts scanning from zero each time despite having a cursor field. That may be intentional simplification or a missed update causing first-fit behavior and fragmentation pressure.
- If the IEDR delete fails, bits are not cleared, preventing software reuse but potentially leaking capacity until reset.
- Bitmap operations are not locally locked and rely on caller serialization.

## Test Signals

Validate resource presence and sane `index_range / usage_bit_count` values for every entry type, exact-fit and near-end allocation cases, exhaustion, free after IEDR success/failure, repeated allocate/free reuse, mixed entry-type isolation, large entry_count requests requiring multiple bits, and KVDL users such as ACL action sets and IPv6 address storage on Spectrum-2/3/4.
