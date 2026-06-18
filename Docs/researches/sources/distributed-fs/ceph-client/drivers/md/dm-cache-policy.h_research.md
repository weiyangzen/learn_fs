# sources/distributed-fs/ceph-client/drivers/md/dm-cache-policy.h

## Purpose
`dm-cache-policy.h` defines the public internal contract implemented by DM cache replacement policies and consumed by the cache target. It describes policy work operations, the policy vtable, and the policy type registration format.

## Important APIs, Types, and Functions
`enum policy_operation` defines `POLICY_PROMOTE`, `POLICY_DEMOTE`, and `POLICY_WRITEBACK`. `struct policy_work` carries an operation plus origin and cache block identifiers. `struct dm_cache_policy` is the vtable for lookup, optional immediate-work lookup, background work issue/complete, dirty state updates, metadata load/invalidate, hint access, residency, tick, config, and migration control. `struct dm_cache_policy_type` describes named policy plugins with version, alias target, hint size, owner module, and create callback. The exported registry declarations are `dm_cache_policy_register()` and `dm_cache_policy_unregister()`.

## Control Flow
Policies are instantiated by the registry, then the cache target repeatedly calls lookup on I/O, asks for background work, completes work, updates dirty state, and periodically calls tick. Metadata load calls `load_mapping()` before normal I/O. During shutdown or commit, the target can query hints and config/status.

## State and Persistence
The header owns no state. It defines how policies expose volatile decisions and how they provide persistent hint values. Policy name, major version, and hint size are persisted by metadata to decide whether saved hints are reusable.

## Dependencies and Integration Points
It includes cache block types and `linux/device-mapper.h` for DM status emission and kernel types. It is included by policy implementations, the policy registry, the background tracker, cache metadata, and the cache target.

## Risks and Edge Cases
The lookup contract says it must not block and may return `-EWOULDBLOCK`; policy implementations need to honor block-layer constraints. `complete_background_work()` requires the exact work pointer originally returned, not a copy, because implementations may embed it in tracked state. Hint size is currently constrained by the registry to 0 or 4 bytes.

## Test Signals
Compile and runtime tests should validate every policy implementation fills required callbacks, lookup does not sleep in request context, background work pointer identity is preserved, dirty state callbacks match metadata dirty bits, and policy status/config behavior remains stable for user space.
