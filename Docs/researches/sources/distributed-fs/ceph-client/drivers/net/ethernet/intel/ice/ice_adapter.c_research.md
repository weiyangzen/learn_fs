# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_adapter.c

## Purpose
`ice_adapter.c` manages shared `struct ice_adapter` objects across PFs belonging to the same physical adapter. This lets multiple PCI functions coordinate shared hardware resources such as PTP and Tx queue context registers.

## Important APIs, Types, And Functions
The file owns a global `DEFINE_XARRAY(ice_adapters)` and `DEFINE_MUTEX(ice_adapters_mutex)`. `ice_adapter_index()` computes a 64-bit adapter identity: most devices use PCI DSN with the fixed-index bit cleared, while E825C device IDs use a fixed index because each NAC can have a unique DSN while still sharing a clock source. `ice_adapter_xa_index()` folds the 64-bit identity on 32-bit systems.

`ice_adapter_new()` allocates and initializes refcount, spinlocks, port-list mutex, and port list. `ice_adapter_get()` loads or creates a shared adapter under the global mutex, reserves the xarray slot before allocation, increments refcount on reuse, and stores new adapters. `ice_adapter_put()` decrements the refcount and erases/frees the adapter when the last PF releases it.

## Control Flow
PF probe obtains an adapter via `ice_adapter_get(pdev)` and stores it in `pf->adapter`. Remove calls `ice_adapter_put(pdev)`. All global xarray mutation is serialized by `ice_adapters_mutex`. Adapter freeing warns if the shared ports list is not empty, then destroys its mutex.

## State And Persistence
The shared adapter state is runtime-only. It includes `refcount`, PTP GLTSYN time spinlock, Tx queue context spinlock, optional control PF pointer, shared ports list, and cached 64-bit index used for collision detection. No state survives driver unload.

## Dependencies And Integration Points
The file depends on Linux xarray, mutex, refcount, spinlock, PCI DSN, ICE device IDs, and `struct ice_adapter` from `ice_adapter.h`. It integrates with `ice.h` through `pf->adapter` and helper code such as `ice_get_primary_hw()`, which may use the adapter control PF.

## Risks And Test Signals
Risks include xarray index collisions on 32-bit systems, incorrect E825C sharing assumptions, reference leaks, freeing while ports remain linked, and missing `ice_adapter_put()` on probe unwind. Test signals include multi-PF probe/remove ordering, E825C dual-NAC behavior, lockdep coverage for shared locks, and refcount/xarray warnings on module unload.
