# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/run.go

Purpose: orchestrates the daily S3 lifecycle replay worker. It runs one bounded pass over meta-log events per shard, dispatches due lifecycle deletes, invokes full-bucket walker partitions for cold-start/recovery/walker-only rules, persists cursors, and publishes observability.

Important APIs/types: `LifecycleClient`, `WalkerFunc`, `Config`, `Run`, `summarizeShardCursorLag`, `computeGlobalStartTsNs`, `startSharedSubscription`, `validate`, `runShard`, `saveCursorAndPublish`, `walkerDue`, `drainShardEvents`, and `processMatches`.

Control flow: `Run` validates config, freezes `runNow`, snapshots the lifecycle engine, computes replay hash/max TTL, optionally starts one shared metadata subscription from the minimum shard cursor, fans out events by shard, runs all shard goroutines, cancels/drains the reader, logs a stable heartbeat, and returns the first shard error. `runShard` loads cursor, computes replay/promoted hashes, handles no replay rules with walker-only save, runs recovery/cold-start walker when hashes changed or cursor is absent, rewinds on recovery, optionally runs steady-state walker under `WalkerInterval`, drains shard events, saves cursor with a fresh timeout context, and publishes gauges.

State and persistence behavior: per-shard cursor state is authoritative. `TsNs` advances only through events with no skipped future-due matches; it freezes before not-yet-due work. `RuleSetHash` and `PromotedHash` detect rule edits and partition flips. `LastWalkedNs` throttles walker load and is updated only when a walker fires. Metrics include shard duration, scanned events, dispatch counts, limiter wait, cursor min timestamp, and last walked timestamp.

Dependencies and integration points: integrates lifecycle engine snapshots/partitioning, meta-log reader, router, filer client, lifecycle delete RPC client, cursor persister, sibling lister, bootstrap walker callback, SeaweedFS stats, glog, and rate limiter.

Risks: correctness relies on shared subscription fanout not blocking; every shard channel must be drained. `validate` requires fields even if direct `runShard` tests omit them, so embedded callers should use `Run`. `processMatches` treats transport errors as halted without returning an error, causing cursor persistence at last safe point. `dispatchWithRetry` nil response risk can panic. Negative `RetentionWindow` is treated as fallback because only `<=0` is checked; tests use this as a sentinel. Save uses a background timeout context to survive canceled pass contexts, but if save fails the next run replays.

Test signals: covered by multiple focused tests in this subset: cursor summary, process matches, walker recovery, walker interval, and walk buckets. Full shared-subscription behavior is not directly covered by the listed tests.
