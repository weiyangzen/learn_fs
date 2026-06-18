# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.h

## Purpose
`glusterd-locks.h` declares the management v3 lock object, valid lock entity descriptor, lifecycle hooks, lock/unlock APIs, multi-lock helpers, and stale-lock timer callback used across GlusterD management code.

## Important APIs, Types, And Functions
`glusterd_mgmt_v3_lock_obj` stores the UUID of the lock owner. `glusterd_valid_entities` describes each entity type name and whether locks should be held by default for that type. The public API initializes and tears down the lock and timer dicts, acquires/releases single locks by key and type, acquires/releases multiple entity locks from a transaction dict, and exposes `gd_mgmt_v3_unlock_timer_cbk()` for timer registration.

## Control Flow
Management handlers and syncop code include this header to acquire local locks before transaction phases and release them after completion. The multi-lock functions interpret transaction dictionaries containing keys such as `volname`, `volcount`, `volname1`, `hold_snap_locks`, and similar snap/global variants.

## State And Persistence Behavior
The header defines state shape only. Runtime instances live in `glusterd_conf_t.mgmt_v3_lock` and `glusterd_conf_t.mgmt_v3_lock_timer`; they are in-memory dictionaries and are not persisted by this interface.

## Dependencies And Integration Points
Consumers must provide Gluster types such as `dict_t`, `uuid_t`, `gf_boolean_t`, and `uint32_t` through surrounding includes. The header is consumed by management RPC handlers, syncop transaction code, startup/shutdown initialization, and statedump diagnostics.

## Risks
The API accepts raw `char *type` values and only validates them in the C implementation. Callers must pass stable transaction dicts with the exact key naming convention expected by multi-lock functions. Adding a new lock entity requires coordinated updates to the implementation's valid type table, max entity constant, transaction dict builders, RPC handlers, and tests.

## Test Signals
Compile and integration tests should ensure all declared functions match implementation signatures, lock object UUID storage is statedump-readable, multi-lock key conventions remain stable, and timer callback linkage remains valid for `gf_timer_call_after()`.
