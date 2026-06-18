# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/walk_buckets_test.go

Purpose: unit tests for shard-filtered bucket walking.

Important APIs/types: `recordingDispatcher`, `fixedShardEntries`, `snapshotForBucketRule`, and tests for `WalkBuckets`/`entryShardID`.

Control flow: tests construct entries in target and non-target shards, compile active expiration rules, run `WalkBuckets`, and assert only target-shard paths dispatch. Additional tests assert nil guards, first-error-return while processing later buckets, pre-canceled context handling, and MPU `DestKey` shard selection.

State and persistence behavior: none directly; uses in-memory bootstrap entries.

Dependencies and integration points: exercises lifecycle shard hashing, engine snapshot activation, and bootstrap walker dispatch integration.

Risks: helper `fixedShardEntries` brute-forces names and could be slow if shard count/hash changes dramatically, but bounded attempts are generous. It does not model persisted checkpoints.

Test signals: good coverage for per-shard partitioning, which prevents duplicate lifecycle deletes across daily-run workers.
