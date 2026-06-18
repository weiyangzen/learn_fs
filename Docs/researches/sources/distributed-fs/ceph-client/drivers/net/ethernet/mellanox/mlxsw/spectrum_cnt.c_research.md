<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.c

## Purpose
`spectrum_cnt.c` implements the Spectrum counter allocator and devlink resource accounting for hardware counter banks. It divides the global counter pool into flow and RIF sub-pools, allocates contiguous counter entries sized by hardware resource data, and exposes active usage through devlink resource occupancy callbacks.

## Important APIs, Types, and Functions
The central types are `struct mlxsw_sp_counter_pool` and `struct mlxsw_sp_counter_sub_pool`. Public functions are `mlxsw_sp_counter_resources_register()`, `mlxsw_sp_counter_pool_init()`, `mlxsw_sp_counter_pool_fini()`, `mlxsw_sp_counter_alloc()`, and `mlxsw_sp_counter_free()`. Static helpers register per-resource occupancy callbacks and derive sub-pool base indexes, entry sizes, and sizes from devlink and core resource values.

## Control Flow
Resource registration first reads `COUNTER_POOL_SIZE` and `COUNTER_BANK_SIZE`, registers the top-level devlink counter resource, then registers subresources according to the statically configured bank counts. Runtime pool initialization allocates a flexible `mlxsw_sp_counter_pool`, copies the static sub-pool descriptors, reads configured devlink resource sizes, allocates a bitmap covering the whole counter pool, and registers occupancy callbacks for the top resource and each subresource. Allocation locks the bitmap, scans the requested sub-pool range for the next zero bit, verifies that the full hardware entry size fits before the sub-pool stop index, sets all bits in the entry, and increments atomic occupancy counters. Free clears the same number of bits and decrements occupancies.

## State and Persistence Behavior
State is in `mlxsw_sp->counter_pool`, the allocation bitmap, per-sub-pool base indexes, entry sizes, and atomic active-entry counters. No filesystem persistence exists. Hardware counter indexes are persistent only while the driver instance and corresponding offloaded objects hold them.

## Dependencies and Integration Points
The allocator is used by flow, RIF, nexthop, and devlink dpipe counter users through the public header. It depends on core resources `COUNTER_POOL_SIZE`, `COUNTER_BANK_SIZE`, `COUNTER_SIZE_PACKETS_BYTES`, and `COUNTER_SIZE_ROUTER_BASIC`, and on devlink resource registration/occupancy APIs.

## Risks and Edge Cases
Sub-pool sizes can contain a non-integer number of counter entries, so the overflow check after `find_next_zero_bit()` is essential. Allocation does not validate `sub_pool_id` beyond array indexing, so callers must pass a valid enum. Free only checks against global pool size; callers must free with the same sub-pool type and index returned by allocation. Resource registration can partially register subresources without local rollback if a later register call fails, relying on higher-level devlink teardown behavior.

## Test Signals
Signals include devlink resource tree sizing for the counter pool and flow/RIF children, occupancy increments/decrements when flow/RIF counters are enabled, `-ENOBUFS` when sub-pools fill, and no WARNs from `mlxsw_sp_counter_pool_fini()` for active entries or non-empty bitmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.c -->
