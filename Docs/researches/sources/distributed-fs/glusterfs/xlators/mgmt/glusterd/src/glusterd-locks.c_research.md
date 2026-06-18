# sources/distributed-fs/glusterfs/xlators/mgmt/glusterd/src/glusterd-locks.c

## Purpose
`glusterd-locks.c` implements GlusterD management v3 local lock ownership. It tracks transaction locks for volumes, snapshots, and global entities, provides single and multi-entity lock/unlock operations, and attaches timers that eventually clear stale locks.

## Important APIs, Types, And Functions
`valid_types[]` defines lockable entity classes: `vol` defaults to locked, while `snap` and `global` default to not held unless the transaction dict requests them. Public lifecycle functions are `glusterd_mgmt_v3_lock_init()`, `glusterd_mgmt_v3_lock_fini()`, `glusterd_mgmt_v3_lock_timer_init()`, and `glusterd_mgmt_v3_lock_timer_fini()`. Public lock APIs are `glusterd_mgmt_v3_lock()`, `glusterd_mgmt_v3_unlock()`, `glusterd_multiple_mgmt_v3_lock()`, and `glusterd_multiple_mgmt_v3_unlock()`. `gd_mgmt_v3_unlock_timer_cbk()` is the stale-lock timeout callback.

Static helpers include `glusterd_mgmt_v3_is_type_valid()`, `glusterd_get_mgmt_v3_lock_owner()`, `glusterd_release_multiple_locks_per_entity()`, `glusterd_acquire_multiple_locks_per_entity()`, `glusterd_mgmt_v3_lock_entity()`, and `glusterd_mgmt_v3_unlock_entity()`.

## Control Flow
Startup initializes two dicts in `glusterd_conf_t`: `mgmt_v3_lock` for `glusterd_mgmt_v3_lock_obj` entries and `mgmt_v3_lock_timer` for associated `gf_timer_t *` pointers. A single lock call validates `name` and `type`, constructs the key `<name>_<type>`, checks whether an owner UUID already exists, allocates a lock object with the requester UUID, stores it in `mgmt_v3_lock`, duplicates the key for timer data, schedules `gd_mgmt_v3_unlock_timer_cbk()` after `priv->mgmt_v3_lock_timeout`, resets the timeout to `GF_LOCK_TIMER`, and stores the timer pointer in `mgmt_v3_lock_timer`.

Unlock validates the key and owner UUID, deletes the owner from `mgmt_v3_lock`, retrieves and cancels the timer, removes the timer dict entry, and resets `volinfo->stage_deleted` if a delete transaction failed after staging the volume. Owner mismatch and missing-lock cases are rejected.

Multi-lock acquisition walks `valid_types[]`. For each type, it evaluates `hold_<type>_locks` from the transaction dict, then locks either `<type>name` or numbered `<type>nameN` entries based on `<type>count`. If any lock fails, it releases the locks already acquired for that entity and then releases all previously acquired entity types. Multi-unlock mirrors this process but attempts all entity types and records the last failure.

The timer callback receives the duplicated key, deletes the lock object, optionally deletes DEBUG backtrace metadata, retrieves its timer pointer, frees timer data, cancels the timer, and logs cleanup.

## State And Persistence Behavior
Lock state is in-memory only under `glusterd_conf_t`. It is not persisted across GlusterD restarts. Timer timeout state uses `conf->mgmt_v3_lock_timeout`, which can be temporarily overridden by management handlers using a request dict `timeout`, then reset after scheduling. DEBUG builds also store a `debug.last-success-bt-<key>` string in the lock dict. Unlock may mutate volume runtime metadata by clearing `stage_deleted` if the volume still exists.

## Dependencies And Integration Points
The file depends on Gluster dicts, UUID utilities, timers, volume lookup, logging message IDs, and the management v3 RPC handlers in `glusterd-mgmt-handler.c`. Management initiation code and syncop code call these APIs locally and remotely. Statedump code inspects `priv->mgmt_v3_lock`. The lock key contract is dictated by transaction dictionaries produced by volume, snapshot, and global operation paths.

## Risks
There is a fragile constant relationship between `GF_MAX_LOCKING_ENTITIES` and the length of `valid_types[]`; adding a type without updating the constant can make successful multi-locks look failed. The dicts are global process state, so callers rely on the big GlusterD lock or external serialization rather than internal per-dict locking. Error paths around timer storage can leave an owner lock without a valid timer if partial setup changes are not fully undone. The timer callback clears locks without checking transaction liveness, so very long operations need correct timeout extension. Lock key formatting with `PATH_MAX` rejects truncation but still depends on names fitting within that bound.

## Test Signals
Tests should cover valid and invalid entity types, single lock/unlock success, already-held lock returning `EG_ANOTRANS`, owner mismatch rejection, timer cancellation on unlock, stale timer unlock, timeout override reset, single and counted multi-lock dict layouts, rollback on partial multi-lock failure, global/snap `hold_*_locks` toggles, `stage_deleted` reset on unlock, and DEBUG backtrace key cleanup where applicable.
