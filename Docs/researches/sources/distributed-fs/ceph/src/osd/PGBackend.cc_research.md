# sources/distributed-fs/ceph/src/osd/PGBackend.cc

## Purpose
`PGBackend.cc` implements shared backend behavior for replicated and erasure-coded PG backends. It handles recovery-delete message batching and replies, rollback/rollforward/trim interpretation of log modification descriptors, temp object cleanup, object listing and attribute helpers, rollback object stashing/restoration, partial-write last-complete tracking for optimized EC behavior, backend construction, and scrub-map scanning.

## Important APIs and Functions
Recovery delete support is implemented by `recover_delete_object()`, `send_recovery_deletes()`, `handle_message()`, `handle_recovery_delete()`, and `handle_recovery_delete_reply()`. The sender batches deletes by `osd_max_push_cost` and `osd_max_push_objects`; replicas remove missing objects and reply; the primary marks peers recovered and calls `on_global_recover()` once no peer or local missing entry remains.

Rollback and trim logic centers on `rollback()`, `rollforward()`, `trim()`, and `trim_after_remove()`. Local visitor classes walk `ObjectModDesc` entries and translate high-level log changes into `ObjectStore::Transaction` operations: truncate appended data, restore attributes, unstash removed objects, remove created objects, update snap mappings, clone old extents back from rollback generations, trim rollback generations, and handle EC omap journal entries.

Storage helpers include `try_stash()`, `remove()`, `on_change_cleanup()`, `objects_list_partial()`, `objects_list_range()`, `objects_get_attr()`, `objects_get_attrs()`, `rollback_setattrs()`, `rollback_append()`, `rollback_stash()`, `rollback_try_stash()`, `rollback_extents()`, and `trim_rollback_object()`. `partial_write()` updates `pg_info_t::partial_writes_last_complete` for nonprimary EC shards that were not written by an optimized partial write. `build_pg_backend()` chooses `ReplicatedBackend` or `ECSwitch` and loads the erasure-code plugin for EC pools. `be_scan_list()` builds scrub-map metadata and invokes backend-specific deep scrub.

## Control Flow
Incoming backend messages first pass through `handle_message()`, which consumes recovery-delete messages before delegating unknown messages to `_handle_message()` implemented by concrete backends. Delete recovery starts when a recovering primary sees peers missing an object that is a delete; it records per-peer deletes in the recovery handle, then `run_recovery_op()` implementations eventually call `send_recovery_deletes()`. Replies update peer recovery state and may complete global recovery.

Rollback flow is visitor-driven. A PG log entry's `mod_desc` is asserted rollback-capable, visited, and each operation prepends or appends transaction fragments so object state returns to the prior version. Trim/rollforward similarly visits modification descriptors but removes no-longer-needed rollback objects or applies EC omap journal cleanup. Scrub scanning is incremental: first stat/getattrs populate a `ScrubMap::object`; deep scrub may return `-EINPROGRESS`; otherwise the builder advances to the next object.

## State and Persistence
`PGBackend` stores `cct`, `store`, `coll`, collection handle, parent listener, and `temp_contents`. Persistent effects are all `ObjectStore::Transaction` operations against `coll`, normal object generations (`NO_GEN`), rollback generations (`version_t`), shard-specific `ghobject_t`s, omap headers/keys, snap mappings, and temp collection objects. Recovery delete state is transient in `RecoveryHandle::deletes`, while partial-write state is persisted through updated `pg_info_t`.

## Dependencies and Integration Points
The implementation depends on concrete backend classes (`ReplicatedBackend`, `ECSwitch`), erasure-code plugin registry, `PGLog`, `ObjectStore`, scrub map types, OSD map features, recovery delete messages, `ObjectModDesc` visitor APIs, `PGBackend::Listener` callbacks, `C_GatherBuilder`, and Ceph logging/config. It is called by PG recovery, PG log trimming, rollback, scrub, and backend message dispatch.

## Risks
Rollback correctness is highly sensitive to EC optimized writes, shard-specific object sizes, written-shard sets, and OI attribute versions. `rollback_setattrs(only_oi=true)` decodes and rewrites object_info; malformed or missing `OI_ATTR` would be serious. Recovery delete completion depends on missing sets being updated before checking global completion. `objects_list_partial()` must filter generated rollback/temp/meta objects correctly. `build_pg_backend()` asserts that EC plugin loading succeeds, so profile/config errors abort. Many unexpected store errors abort rather than propagate.

## Test Signals
Tests should cover recovery delete batching/replies, rollback of append/setattrs/remove/create/snap/extents, EC optimized written/unwritten shard behavior, omap journal trim/delete cases, partial-write last-complete transitions, temp cleanup on interval changes, object list filtering in fixed and legacy collection-list modes, attr helpers, backend construction for replicated and EC pools, and scrub scan handling of ENOENT/EIO/EINPROGRESS.
