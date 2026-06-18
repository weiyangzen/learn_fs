# sources/cloud-native/nydus/storage/src/backend/qps.rs

## Purpose
This module implements a simple cloneable token-bucket QPS limiter used by backend retry logic to throttle source-backend fallback requests.

## Important APIs, Types, and Functions
`QpsLimiter::new` creates a limiter with capacity and refill rate equal to the configured QPS. `try_acquire` and `try_acquire_tokens` attempt non-blocking token consumption. `acquire` and `acquire_tokens` block until enough tokens are available and return whether waiting occurred. `current_tokens` reports refilled available tokens, and `qps` reports the configured rate. `QpsLimiterInner::refill` computes elapsed time and caps tokens at capacity.

## Control Flow
Fast paths lock, refill, and consume tokens if available. Blocking paths first try the fast path, then wait on a condition variable with a timeout computed from token shortage and rate. There is no producer thread; token availability advances when callers wake by timeout or inspect the limiter.

## State and Persistence Behavior
All state is in-memory inside `Arc<Mutex<QpsLimiterInner>>`. Clones share token state. The limiter does not persist across process restarts and does not expose dynamic reconfiguration.

## Dependencies and Integration Points
`BACKEND_QPS_LIMITER` in `mod.rs` creates a global 1 QPS limiter for direct source fallback after proxy rate limits or final on-demand retry. The implementation uses only standard synchronization/time primitives.

## Risks
`acquire_tokens` with `count > capacity` can block forever because the bucket can never accumulate enough tokens. The condition variable is only notified by timeout, not by explicit refill events, which is acceptable but means wait granularity depends on timeout calculation. Floating-point token accounting can cause small timing variance. Mutex poisoning is unhandled.

## Test Signals
Tests cover construction, initial tokens, exhaustion, refill timing, blocking acquisition, multi-token acquisition, approximate QPS accuracy, low-QPS behavior, concurrent acquisition, and return values indicating rate-limited waits.
