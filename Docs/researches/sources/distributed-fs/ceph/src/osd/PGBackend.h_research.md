# sources/distributed-fs/ceph/src/osd/PGBackend.h

## Purpose
`PGBackend.h` declares the abstract backend interface that concrete replicated and erasure-coded implementations use to provide object IO, replication, recovery, scrub, repair, rollback, and omap behavior for a PG. It also declares the callback interface (`Listener`) that lets a backend call back into its owning PG without depending on a concrete PG class.

## Important APIs, Types, and Members
`PGBackend::Listener` is the central integration surface. It provides recovery callbacks (`on_local_recover`, `on_global_recover`, `on_peer_recover`, `begin_peer_recover`, failed/canceled pulls, remove missing object), locking/refcount helpers, context blessing, message sending, transaction queueing, map/interval access, acting/backfill shard sets, missing/info/log access, object context and lock management, operation logging, snap mapping, committed/version/stat updates, recovery scheduling, timers, identity, connection and monitor command helpers, perf counters, cluster log streams, full checks, repaired stat increments, byte accounting, scrub preemption, and EC listener access.

Backend lifecycle and recovery APIs include `open_recovery_op()`, `run_recovery_op()`, `recover_delete_object()`, `send_recovery_deletes()`, `recover_object()`, `can_handle_while_inactive()`, `handle_message()`, `_handle_message()`, `check_recovery_sources()`, `on_change_cleanup()`, `on_change()`, and `clear_recovery_state()`. Predicate APIs expose recoverability/readability, EC chunk sizing, CRC encode/decode support, object-to-shard sizing, nonprimary/hinfo/optimized-EC flags, EC encode/decode helpers, EC omap journal operations, and omap iteration/get/check operations.

Write and log APIs include `submit_transaction()`, `call_write_ordered()`, `try_stash()`, `rollback()`, `rollforward()`, `trim()`, `trim_after_remove()`, `partial_write()`, and `remove()`. Object access APIs include `objects_list_partial()`, `objects_list_range()`, attr getters, sync/local/async reads, optional readv, extent-to-shard conversion, scrub scans, deep scrub, and backend factory `build_pg_backend()`.

## Control Flow
The parent PG constructs a concrete backend through `build_pg_backend()` and then calls backend methods while holding PG locks as documented. Client writes are translated by concrete backends into `submit_transaction()` calls with log entries, stats deltas, hitset history, commit callbacks, tids, reqids, and `OpRequestRef`. Recovery opens a backend-specific `RecoveryHandle`, calls `recover_object()` or `recover_delete_object()` for objects, then `run_recovery_op()` sends or applies the accumulated work. Incoming messages call shared `handle_message()` before concrete `_handle_message()`.

Rollback/trim flows are shared by the base implementation and invoked through `PG::PGLogEntryHandler`. Scrub flows call `be_scan_list()` for common metadata scanning and backend-specific `be_deep_scrub()` for data verification. Omap APIs abstract replicated local omap and EC omap-journal behavior behind one PG-facing interface.

## State and Persistence
The base class stores context, object store pointer, collection id, collection handle reference, parent listener, and a set of temp objects to remove on interval reset. Concrete subclasses own replication/EC-specific pending operations, caches, and recovery state. Persistence is expressed entirely through `ObjectStore::Transaction`, object generations, omap updates, PG log entries, snap mappings, and queued transactions through the parent listener.

## Dependencies and Integration Points
The header depends on EC support types, extent cache, object store, scrubber types, log client, PG transactions, coroutine handles, `PGLog`, `OSDMap`, and many OSD data types. It is the seam between `PG`/`PeeringState` and concrete object-storage protocols: replicated backends, EC switch/backends, scrub/repair, recovery reservations, OSD messaging, object contexts, and object store transactions all meet here.

## Risks
`Listener` is very large and assumes calls occur under the same PG locks as parent code. Mis-blessed contexts or lock misuse can race PG destruction or interval changes. The base class provides default false/no-op implementations for some EC-only methods; a concrete backend must override all methods relevant to its pool type. Temp object tracking must stay synchronized with actual temp collection contents or interval cleanup can leak objects. Omap behavior differs significantly between replicated and optimized EC pools, so callers must not assume local-object semantics for all backends.

## Test Signals
Interface tests should use mock listeners to verify callback ordering for recovery, transaction queueing, locking, and message sending. Concrete backend tests should cover replicated and EC transaction submission, recovery handles, message dispatch while inactive, interval cleanup, rollback/trim through `PGLogEntryHandler`, omap APIs, scrub scans/deep scrub, EC encode/decode and shard sizing, read paths, write ordering callbacks, and auto-repair support flags.
