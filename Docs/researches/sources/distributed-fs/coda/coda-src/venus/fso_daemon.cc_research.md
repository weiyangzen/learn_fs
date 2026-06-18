# sources/distributed-fs/coda/coda-src/venus/fso_daemon.cc

Purpose: implements the Venus filesystem-object daemon that periodically reclaims fsobjs and blocks, garbage-collects dying objects, recomputes priorities, and flushes volatile reference data to recoverable storage.

Important APIs and flow: `FSOD_Init` starts a `vproc` named `FSODaemon`. `FSODaemon` registers on `fsdaemon_sync`, wakes every five seconds or on explicit signal, runs `FSDB->GetDown` every 30 seconds, and calls `FSDB->FlushRefVec` every 90 seconds. `FSOD_ReclaimFSOs` forces the next reclaim by resetting `LastGetDown` and signaling the daemon. `fsdb::RecomputePriorities` recomputes priorities only when references changed or when forced. `GarbageCollect` walks `delq`, checks `DYING`, skips non-GC-able/busy objects, and calls `GC`. `GetDown` combines GC, priority recomputation, `ReclaimFsos`, and `ReclaimBlocks` against free margins. `FlushRefVec` persists `LastRef` with `rvmlib_set_range`.

State and persistence: daemon state is transient wake timing plus persistent FSDB metadata touched in transactions. `GetDown` must run inside a transaction; `FlushRefVec` opens its own transaction because ordinary object references do not persist `LastRef` immediately.

Dependencies and integration: depends on `vproc` scheduling, `FSDB`, replacement priority queues, object deletion queues, RVM recovery primitives, and worker/daemon registration.

Risks and test signals: risks are reclaim while objects remain pinned/open, stale priority calculations, negative free counts, long transactions during GC, and missed forced reclaim signals. Tests should stress cache overflow, busy dying objects, block and fso margin enforcement, priority aging after references, and daemon wake timing.
