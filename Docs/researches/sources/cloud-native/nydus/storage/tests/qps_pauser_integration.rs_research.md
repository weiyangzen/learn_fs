# sources/cloud-native/nydus/storage/tests/qps_pauser_integration.rs

Purpose: integration tests for storage backend QPS limiting and pausing behavior under concurrent and time-dependent scenarios.

Important APIs/types/functions: imports `nydus_storage::backend::qps::QpsLimiter` and `nydus_storage::backend::pauser::Pauser`. QPS tests cover `new`, `acquire`, `try_acquire`, and `acquire_tokens`. Pauser tests cover `new`, `set_pause`, `wait`, and `clear_pause`.

Control flow: QPS tests spawn worker threads or loops that acquire tokens under sustained load, consume the initial burst bucket, mix single-token and multi-token requests, and verify the boolean "was limited" indication. Pauser tests set a pause before spawning request threads, assert they remain blocked briefly, then wait for expiration; another test clears a long pause and asserts prompt unblocking.

State and persistence: no persistence. Shared state is in `Arc<QpsLimiter>`, `Arc<AtomicUsize>`, and `Arc<AtomicBool>`. Timing and token bucket state are in-memory.

Dependencies and integration points: validates the behavior expected by backend request paths and retry/fallback logic that need to throttle source/backend access. Uses std threading, atomics, `Duration`, and `Instant`.

Risks: time-based assertions are inherently sensitive to loaded CI machines. The sustained throughput test uses generous bounds but still assumes scheduler behavior over two seconds. `all_started` in the pauser test is stored but not meaningfully asserted. The "mixed token" test verifies accounting but not elapsed rate bounds.

Test signals: these are direct integration tests and provide useful coverage for concurrency and operator pause/resume behavior. They complement unit tests by checking real thread contention and elapsed time behavior.
