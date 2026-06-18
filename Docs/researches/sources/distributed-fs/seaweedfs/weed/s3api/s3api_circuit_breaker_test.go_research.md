# sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker_test.go

Purpose: Tests circuit breaker limit enforcement under concurrent access.

Important APIs/types/functions: `TestLimitCase`, `TestLimitCases`, `TestLimit`, and `doLimit`.

Control flow: each case builds an `s3_pb.S3CircuitBreakerConfig` with global and bucket limits for either count or bytes, loads it into a fresh `CircuitBreaker`, then launches multiple goroutines calling `limit`. Successful calls record rollback functions, and after all goroutines finish the test runs rollbacks and asserts expected success count.

State and persistence: no filer persistence. Tests in-memory `limitations` and `counters` maps plus atomic counter increments/decrements.

Dependencies and integration: uses S3 constants for action/limit key concatenation, `s3err` to detect success, and `http.Request{ContentLength:fileSize}` for byte tests.

Risks: test uses a bucket string with slash and duplicate map assignment in global actions, but it still exercises the intended key shapes. It does not verify wrapper-level upload throttling, metrics, rollback after handler panic, or unknown content length.

Test signals: useful concurrency regression signal for the core atomic counter path.
