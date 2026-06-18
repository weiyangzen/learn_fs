# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walker_dispatcher.go

Purpose: adapts the lifecycle delete RPC client to the bootstrap walker's `Dispatcher` interface. It lets full-bucket walks drive the same server-side delete path as meta-log replay.

Important APIs/types: `WalkerDispatcher` with `Client` and optional shared `Limiter`; method `Delete(ctx, action, entry) error`.

Control flow: `Delete` validates receiver/client/action/entry, chooses `entry.Path` as RPC object path, verifies MPU init entries have `DestKey` but still dispatches `.uploads/<id>` path, builds `LifecycleDeleteRequest` without `ExpectedIdentity`, waits on limiter if present, calls `LifecycleDelete`, increments metrics, accepts DONE/NOOP_RESOLVED/SKIPPED_OBJECT_LOCK, and turns transport errors, nil responses, and unresolved outcomes into errors.

State and persistence behavior: no persistence. Returning errors is part of walker checkpoint semantics: the walk should halt and retry instead of silently skipping unresolved deletes.

Dependencies and integration points: uses bootstrap dispatcher contract, engine compiled actions, lifecycle proto, stats counters, and rate limiter. Shares `toProtoActionKind` with daily-run dispatch file.

Risks: no transport retry here, unlike meta-log dispatch. That may be intentional because walker checkpointing can retry later, but transient errors halt a full walk. Nil `ExpectedIdentity` relies on server-side semantics that treat it as bootstrap/no-CAS. MPU path handling is easy to break: matching uses destination key elsewhere, dispatch must use upload path.

Test signals: `walker_dispatcher_test.go` covers request shape for non-versioned/versioned/MPU, empty MPU dest guard, accepted/unresolved outcomes, transport/nil response errors, limiter waiting/cancel, and nil guards.
