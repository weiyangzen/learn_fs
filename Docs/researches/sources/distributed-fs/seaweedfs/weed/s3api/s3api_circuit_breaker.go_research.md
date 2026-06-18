# sources/distributed-fs/seaweedfs/weed/s3api/s3api_circuit_breaker.go

Purpose: Provides request concurrency/bytes limiting for S3 API actions, plus upload-specific in-flight throttling and metrics.

Important APIs/types/functions: `CircuitBreaker`, `NewCircuitBreaker`, `LoadS3ApiConfigurationFromBytes`, `loadCircuitBreakerConfig`, `Limit`, `limit`, and `loadCounterAndCompare`.

Control flow: construction reads circuit breaker config from filer with multi-filer failover. Config loading builds a limitations map from global and bucket-specific action count/bytes limits. `Limit` wraps HTTP handlers: for write actions it optionally waits on server-level in-flight upload byte/file limits, increments gauges, then if circuit breaker is enabled calls `limit`. `limit` checks bucket count, bucket bytes, global count, and global bytes in order, collecting rollback functions for increments; wrapper defers rollback after handler or error.

State and persistence: config is persisted in filer under the circuit breaker config path. Runtime counters are in-memory atomic int64 pointers keyed by bucket/action/type. Upload in-flight counters live on `S3ApiServer`; Prometheus-style gauges are updated on increment/decrement.

Dependencies and integration: depends on filer config parsing, mux bucket variables, S3 constants/errors, stats, `sync/atomic`, and `S3ApiServerOption`. It wraps registered S3 routes.

Risks: `ContentLength` can be negative for unknown-length requests, which could reduce byte counters if not guarded in the circuit-breaker byte path. Counter creation uses double-checked locking and atomics; rollback must run for all successful partial increments. Limits are local to the process, not cluster-wide.

Test signals: `s3api_circuit_breaker_test.go` stresses concurrent `limit` calls for bucket/global count and byte limits.
