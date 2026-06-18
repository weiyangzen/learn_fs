# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/dailyrun/dispatch_test.go

Purpose: unit tests for daily-run dispatch retry behavior and protobuf request construction.

Important APIs/types: `fakeLifecycleClient`, `scriptedResp`, `sampleMatch`, and `dispatchWithRetryFast` support tests of `dispatchWithRetry` and `buildDeleteRequest`.

Control flow: fake client returns scripted outcomes/errors and counts calls. Tests assert exact retry counts, outcome propagation, context cancellation behavior, and identity/rule-hash fields.

State and persistence behavior: none. Results influence caller cursor semantics by distinguishing transport errors from server outcomes.

Dependencies and integration points: uses `s3_lifecycle_pb`, lifecycle action keys, and router match identity.

Risks: comments say tests are sped up, but constants are not overridden; retry-exhaustion can take production backoff time. No test covers `(nil, nil)` response panic risk.

Test signals: good guard that server `RETRY_LATER`/`BLOCKED` are surfaced without local retry, preserving daily-run halt/resume design.
