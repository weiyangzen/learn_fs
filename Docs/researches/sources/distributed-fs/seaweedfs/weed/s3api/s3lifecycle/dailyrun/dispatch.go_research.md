# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch.go

Purpose: daily-run delete RPC dispatch helper. It converts router matches into `LifecycleDelete` protobuf requests and retries transient transport errors with bounded jittered backoff.

Important APIs/types: `dispatchWithRetry`, `jitter`, `buildDeleteRequest`, `toProtoActionKind`, and `toProtoIdentity`. Constants define three transport attempts and 200ms-to-5s exponential backoff.

Control flow: `dispatchWithRetry` builds one request, calls `client.LifecycleDelete`, returns server outcomes immediately on successful RPC, short-circuits context cancellation/deadline, retries only transport errors, and sleeps with equal jitter between attempts. `buildDeleteRequest` copies bucket, object path, version id, rule hash bytes, action kind, and optional CAS identity witness.

State and persistence behavior: no persistence. It affects cursor advancement indirectly because callers halt on errors or unresolved outcomes.

Dependencies and integration points: depends on lifecycle proto, `router.Match`, action kind enum, and the `LifecycleClient` interface from `run.go`.

Risks: nil response is not checked here; a client returning `(nil, nil)` would panic when reading `resp.Outcome`. Walker dispatch has a nil-response guard, but daily replay dispatch does not. Random jitter uses package global `math/rand`, which is acceptable for backoff but not deterministic unless tests avoid exact timing. Server outcomes are intentionally not retried in-run.

Test signals: `dispatch_test.go` covers success, transport retries/exhaustion, non-retry of `RETRY_LATER`/`BLOCKED`, context cancellation, and request shape including identity. `jitter_test.go` covers jitter bounds and edge cases.
