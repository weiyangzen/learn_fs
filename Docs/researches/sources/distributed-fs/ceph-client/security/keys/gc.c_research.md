<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/gc.c -->
# sources/distributed-fs/ceph-client/security/keys/gc.c

## Purpose
`gc.c` implements deferred garbage collection for keys, keyring links, expired keys, invalidated keys, and keys whose key type is being unregistered. It lets non-sleeping paths such as `key_put()` schedule cleanup in process context.

## Important APIs, Types, and Functions
Public/internal entry points are `key_schedule_gc()`, `key_set_expiry()`, `key_schedule_gc_links()`, and `key_gc_keytype()`. `key_type_dead` is the replacement type for referenced keys after their real key type unregisters. `key_garbage_collector()` is the workqueue body, `key_gc_timer_func()` schedules expiry-link cleanup, and `key_gc_unused_keys()` destroys unreferenced keys from the graveyard list.

## Control Flow
`key_set_expiry()` records an expiry and schedules GC after the expiry plus `key_gc_delay`, except instant-reap key types. The workqueue scans `key_serial_tree` under `key_serial_lock`, removes unreferenced keys to a graveyard, calls `keyring_gc()` to prune dead links, updates keyring restrictions for unregistering key types, and on the final keytype reap cycle changes still-referenced keys to `.dead` after destroying their payload. Keytype unregister uses three observed GC cycles: mark dead, reap links, then reap keys.

## State and Persistence
GC state is in static `key_gc_next_run`, `key_gc_dead_keytype`, `key_gc_flags`, and persistent local `gc_state`. Keys move from the serial tree to the static graveyard list before destruction. User quota counters, instantiated-key counters, domain tags, LSM state, watch lists, descriptions, and slab allocations are released only after final reference death and required RCU synchronization.

## Dependencies and Integration Points
This file coordinates with `key.c` reference dropping, `keyring.c` link cleanup, LSM hooks, key notifications, the timer API, workqueues, RCU, and key type unregister paths under `key_types_sem`.

## Risks
The reaper relies on lock ordering, memory barriers, and the `KEY_FLAG_USER_ALIVE` handoff from `key_put()`. Keytype unregister is multi-pass by design; shortening it can leave links to destroyed payloads. Timer calculation uses coarse real time and `key_gc_delay`, so tests must not assume immediate removal for non-instant key types.

## Test Signals
Validate expiry, revoke, invalidate, final `key_put()`, and key-type unregister under concurrent keyring search/link workloads. Use lockdep/KASAN/KCSAN with nested keyrings, active watches, removed network key domains, and restricted keyrings. Check `/proc/key-users` quota counters return to baseline after GC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/keys/gc.c -->
