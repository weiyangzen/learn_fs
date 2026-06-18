# sources/distributed-fs/ceph-client/drivers/w1/w1_family.c

## Purpose
W1 family registry implementation. It tracks registered family drivers by family ID and coordinates reconnecting existing slaves when families appear or disappear.

## Important APIs, Types, and Functions
Globals are `w1_flock` and private `w1_families`. Exported APIs include `w1_register_family()`, `w1_unregister_family()`, `w1_family_put()`, and `__w1_family_get()`. `w1_family_registered()` finds a family under the caller-held spinlock.

## Control Flow
Registration checks for duplicate IDs, initializes the family refcount, adds it to the list under spinlock, then calls `w1_reconnect_slaves(newf, 1)` so default-bound slaves can bind to the new driver. Unregistration removes the family from the list, calls `w1_reconnect_slaves(fent, 0)` so attached slaves detach/rebind to default or later rediscovery, then waits until the family refcount drains.

## State and Persistence
State is the in-memory family list and per-family atomic refcount. There is no persistent state.

## Dependencies and Integration Points
Depends on `w1_internal.h`, W1 core reconnect logic, spinlocks, atomics, exports, and module lifecycle of slave drivers. All `module_w1_family()` users depend on this registry.

## Risks and Test Signals
Unregistration waits indefinitely until references drain, so leaks in slave references can block module unload. `w1_family_registered()` assumes `w1_flock` is already held. Test duplicate registration, rollback paths in multi-family modules, reconnect from default to specific driver, unload while slaves are active, and refcount drain behavior.
