# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/fakeserver.go

Purpose: provides a thread-safe fake implementation of the internal S3 lifecycle gRPC server for tests.

Important APIs/types: `Outcome`, constructors `Done`, `NoopResolved`, `RetryLater`, `Blocked`, `SkippedObjectLock`, `FakeLifecycleServer`, `NewFakeLifecycleServer`, `Queue`, `SetDefault`, `SetError`, `Recorded`, and `LifecycleDelete`.

Control flow: the fake holds per-request-key FIFO outcome queues keyed by `(bucket, objectPath, versionId)`, a default outcome, optional transport error, and deep-copied received requests. `LifecycleDelete` checks `err` first and short-circuits without recording, records a cloned request, handles nil request via default, pops queued outcomes, or falls back to default.

State/persistence: all mutable state is in-memory protected by a mutex. `Recorded` returns deep copies so callers cannot mutate internal history.

Dependencies/integration: implements `s3_lifecycle_pb.SeaweedS3LifecycleInternalServer` and uses protobuf `proto.Clone`. It allows worker/router tests to exercise gRPC boundary outcomes without a real S3 server.

Risks: mid-call mutation ordering is intentionally undefined around concurrent `Queue`/`SetDefault`; tests should configure before calls when ordering matters. Nil request handling is defensive rather than production-normal.

Test signals: fakeserver tests cover default, FIFO queues, key isolation, version scoping, delimiter collision avoidance, error short-circuit, recording order, deep copies, nil requests, and concurrent calls.
