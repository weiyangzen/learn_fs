# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_kvdl.c

## Purpose
This file is the generic KVDL allocation wrapper for Spectrum. KVDL is shared hardware key-value storage used by many features for adjacency, tunnel, multicast, IPv6 address, and other object pointers. The wrapper hides generation-specific allocators behind `mlxsw_sp_kvdl_ops` and serializes allocation/free operations.

## Important APIs, Types, And Functions
`struct mlxsw_sp_kvdl` stores the selected ops vector, a mutex, and private allocator storage. Public entry points are `mlxsw_sp_kvdl_init()`, `mlxsw_sp_kvdl_fini()`, `mlxsw_sp_kvdl_alloc()`, `mlxsw_sp_kvdl_free()`, and `mlxsw_sp_kvdl_alloc_count_query()`. Allocation takes an entry type, entry count, and output index; free mirrors type/count/index.

## Control Flow
Initialization allocates the wrapper plus ops-private storage, initializes the mutex, stores the ops pointer from `mlxsw_sp`, assigns `mlxsw_sp->kvdl`, and calls the generation-specific `init()`. Alloc/free lock `kvdl_lock`, call through to `alloc()` or `free()`, and unlock. Finalization calls the backend `fini()`, destroys the mutex, and frees the wrapper.

## State And Persistence
All state is runtime in memory plus hardware allocator state managed by backend ops. The mutex protects allocation metadata, not consumers' higher-level object lifetimes. There is no persistent storage.

## Dependencies And Integration Points
The wrapper is used by IPIP, NVE, multicast routing TCAM, adjacency, and other Spectrum subsystems that need hardware KVDL entries. Backend ops are selected by the device generation in `struct mlxsw_sp`.

## Risks And Edge Cases
The caller is responsible for matching type/count/index on free. `alloc_count_query()` is not locked in this wrapper, so backend implementations must be safe for their own query semantics or callers must tolerate races. Init failure correctly destroys the mutex and frees memory, but callers must avoid using `mlxsw_sp->kvdl` after failed init.

## Test Signals
Check feature allocation under concurrent TC/tunnel/multicast churn, KVDL exhaustion behavior, matching allocation count queries, module unload with no backend leak warnings, and generation-specific backend init/fini coverage.
