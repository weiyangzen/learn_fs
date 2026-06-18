# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets.go

Purpose: daily-run wrapper that runs bootstrap walks across buckets for one shard, filtering entries so each shard only processes its own logical object keys.

Important APIs/types: `WalkBuckets`, `perShardListFunc`, and `entryShardID`.

Control flow: `WalkBuckets` validates snapshot/list/dispatcher, wraps the list function with a shard filter, iterates buckets, checks context cancellation between buckets, calls `bootstrap.Walk`, records the first error, and logs additional bucket errors while continuing. `perShardListFunc` drops nil/out-of-shard entries. `entryShardID` hashes `DestKey` for MPU init entries and `Path` otherwise.

State and persistence behavior: no direct persistence. It relies on `bootstrap.Walk` checkpoint semantics internally but does not persist returned checkpoints in this implementation.

Dependencies and integration points: depends on lifecycle `ShardID`, bootstrap walker, engine snapshots, and glog. Intended to be used as the `WalkerFunc` implementation in `run.go`.

Risks: because checkpoints are not persisted here, a bucket walk error returns first error but next invocation starts over. Continuing after one bucket error improves coverage but can hide repeated failures if logs are missed. Correct shard filtering for MPU requires `DestKey`; missing dest falls back to `.uploads` path, but MPU entries without dest are normally skipped by `FilerListFunc`.

Test signals: `walk_buckets_test.go` covers shard filtering, nil guards, continuing after one bucket error, context cancellation, and MPU dest-key sharding.
