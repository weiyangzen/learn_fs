# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/reader/reader.go

Purpose: subscribes to the filer metadata log, filters events to lifecycle bucket/shard scope, and emits `reader.Event` values to downstream routing.

Important APIs/types: `Event`, `BootstrapVersion`, `Reader`, `Run`, `dispatchOne`, `extractBucketKey`, `LogStartup`, plus `Event.IsCreate` and `IsDelete`. `BootstrapVersion` carries walker-derived version ranking/state for noncurrent evaluation.

Control flow: `Run` validates shard/channel/path inputs, computes `SinceNs` from explicit start or cursor min, calls `SubscribeMetadata`, then processes primary and batched events until EOF/error/context/budget. `dispatchOne` skips nil notifications, extracts bucket/key, filters by shard id or predicate, and sends events respecting context cancellation. `extractBucketKey` reconstructs bucket/key from parent path and entry name, handling deletes with `resp.Directory`, bucket-root events, and paths outside `BucketsPath`.

State/persistence: reader itself does not advance/persist cursors; it uses cursor min as subscription start. Event budget bounds one run.

Dependencies/integration: depends on filer protobuf stream, lifecycle shard hashing, and glog. Downstream router/dispatcher consume emitted events and acknowledge actions.

Risks: path normalization around `/buckets` vs `/buckets/`, deletes with empty new parent, and bucket-root events are subtle. Sending to an unbuffered channel can block; context cancellation handles it.

Test signals: reader tests cover path extraction variants, shard filtering, context cancellation, input validation, event predicates, and startup logging branches.
