# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/bootstrap/walker.go

Purpose: bucket-level lifecycle bootstrap walker. It scans existing bucket entries, evaluates active lifecycle actions against each entry, and dispatches currently due deletes. It handles cold-start/recovery coverage that meta-log replay alone cannot provide.

Important APIs/types: `Entry` is the walker input model, including logical path, MPU destination key, version metadata, delete marker state, tags, and noncurrent rank. `ListFunc` streams entries after a resume marker. `Dispatcher` executes deletes. `Checkpoint` records `LastScannedPath` and `Completed`. `WalkOptions` carries resume and current time. `Walk`, `walkEntry`, `EntryCallback`, and `HasPrefix` are core APIs.

Control flow: `Walk` initializes `now`, creates a checkpoint, calls the list function, skips nil/empty entries, skips ordinary directories, lets MPU init directories through, calls `walkEntry`, and advances `LastScannedPath` only after successful processing. `walkEntry` uses `DestKey` for MPU prefix matching, fetches matching active action keys from the engine snapshot, skips disabled actions, gates action/entry shape so MPU actions only fire on MPU init records and non-MPU actions only fire on object/version records, evaluates due status, dispatches, and increments bootstrap dispatch metrics.

State and persistence behavior: the walker itself returns `Checkpoint`; callers persist it outside this file. The checkpoint intentionally does not advance past a failing entry, allowing retry. It does not persist per-action state.

Dependencies and integration points: depends on lifecycle `EvaluateAction`, engine snapshots, `stats.S3LifecycleBootstrapDispatchCounter`, and a caller-provided list source/dispatcher. Daily-run uses this via `WalkBuckets` and `WalkerDispatcher`.

Risks: list functions must honor `Path <= start` skip semantics or resume can duplicate/delete incorrectly. Versioned siblings share paths, so resume granularity is logical-key level. MPU handling is subtle: match on `DestKey`, dispatch on `.uploads/<id>` path. Missing `DestKey` is skipped to avoid guessing. Date-based actions are processed by regular walks because a dedicated scan-at-date path was not wired.

Test signals: `walker_test.go` covers due/not-due dispatch, multi-action rules, date actions, directory skipping, disabled/inactive actions, dispatch failure checkpointing, resume, MPU destination matching, and shape gates.
