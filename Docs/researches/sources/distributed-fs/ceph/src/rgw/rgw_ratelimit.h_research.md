# sources/distributed-fs/ceph/src/rgw/rgw_ratelimit.h

## Purpose

Implements an in-memory token-bucket style rate limiter for RGW users and buckets, with separate operation and bandwidth counters for read, write, list, and delete traffic. It also manages active/passive limiter maps to bound memory growth.

## Important APIs, Types, and Functions

`OpType` distinguishes `Read`, `Write`, `List`, and `Delete`. `RateLimiterEntry` holds fixed-point token counters and exposes `should_rate_limit()`, `decrease_bytes()`, `giveback_tokens()`, and `compute_delay()`. `RateLimiter` maps string keys to entries, classifies operations from HTTP method/resource, and exposes per-key rate-limit methods. `ActiveRateLimiter` owns two `RateLimiter` instances, a background replacement thread, and `get_active()`/`start()`.

## Control Flow and Data Flow

Each request calls `RateLimiter::should_rate_limit()` with method, key, timestamp, config info, and resource. The limiter skips empty/one-character keys and disabled configs, classifies list operations by query patterns, finds or creates an entry, replenishes tokens based on elapsed time, and returns either zero or a retry delay. Body input/output calls later call `decrease_bytes()` to charge bandwidth debt; failed requests can call `giveback_tokens()` to restore operation tokens.

When the map exceeds 90 percent of the fixed `map_size`, `find_or_create()` flips `replacing` and wakes `ActiveRateLimiter::replace_active()`. The replacement thread switches active maps, waits until the old shared pointer is no longer used by requests, clears it, and resets replacement state.

## State and Persistence Behavior

All state is transient process memory. Token counters are fixed-point scaled by 1000 to preserve fractional refill. No rate-limit state survives RGW restart, and active/passive map replacement intentionally drops old entries.

## Dependencies and Integration Points

Depends on `rgw_common.h`, `RGWRateLimitInfo`, global Ceph config for interval, Ceph time types, logging, `shared_mutex`, condition variables, and threads. It integrates with REST body send/receive paths and request pre-checks that populate user and bucket rate-limit info.

## Risks and Edge Cases

`ActiveRateLimiter` destructor unconditionally joins `runner`; destruction before `start()` would be unsafe. `RateLimiter::clear()` is not protected by `insert_lock` in this header, relying on active/passive pointer isolation. List detection is heuristic based on query substrings. Byte counters are charged after body transfer, so op admission can pass before bandwidth debt is known. Zero limits return no delay in `compute_delay()`, so disabled dimensions must be represented consistently.

## Test Signals

Test fractional refill for low rates, delay computation boundaries, read/write/list/delete classification, bandwidth debt capped at two minutes, token giveback, disabled and empty-key bypass, concurrent insert/find, map replacement while requests hold old shared pointers, and destructor behavior when `start()` was or was not called.
