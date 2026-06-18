<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.h

## Purpose
`spectrum_cnt.h` declares the counter sub-pool IDs and public counter-pool API used by Spectrum flow, router, and devlink inspection code.

## Important APIs, Types, and Functions
The header defines `enum mlxsw_sp_counter_sub_pool_id` with RIF and flow sub-pools, and declares `mlxsw_sp_counter_alloc()`, `mlxsw_sp_counter_free()`, `mlxsw_sp_counter_pool_init()`, `mlxsw_sp_counter_pool_fini()`, and `mlxsw_sp_counter_resources_register()`.

## Control Flow
The header has no execution flow. It establishes the required lifecycle: register devlink resources, initialize the pool during device bring-up, allocate/free indexes for offloaded users, and finish the pool during teardown after all users have released counters.

## State and Persistence Behavior
No state is stored in the header. It references `struct mlxsw_sp` and `struct mlxsw_core` owners whose implementation state is in `spectrum_cnt.c`.

## Dependencies and Integration Points
It includes `core.h` and `spectrum.h`, so users inherit Spectrum core type definitions. The API integrates with offload modules that need packet/byte or router-basic counters without knowing the internal bank layout.

## Risks and Edge Cases
The enum order must match the static sub-pool descriptor array in `spectrum_cnt.c`. Callers must pair alloc/free with the same sub-pool ID and must not use indexes after freeing them.

## Test Signals
Compile coverage validates declarations. Runtime signals come from all counter users successfully allocating and freeing counters, plus devlink resource occupancy matching active offloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_cnt.h -->
