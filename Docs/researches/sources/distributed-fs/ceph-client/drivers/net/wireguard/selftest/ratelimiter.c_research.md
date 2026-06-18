# sources/distributed-fs/ceph-client/drivers/net/wireguard/selftest/ratelimiter.c

Purpose: Provides DEBUG-only init-time tests for the WireGuard handshake ratelimiter.

Important APIs and functions: `wg_ratelimiter_selftest()` drives initialization reference-count checks, skb construction, optional timing tests, capacity tests, and extra uninit underflow tolerance. Helpers include `maximum_jiffies_at_index()`, `timings_test()`, and `capacity_test()`.

Control flow: The selftest initializes the ratelimiter three times, creates IPv4 and optional IPv6 skbs, optionally runs rate timing expectations against token refill intervals, then fills entries up to `max_entries` to verify capacity rejection. It frees skbs and calls uninit four times to check balanced and extra uninit behavior. KASAN/UBSAN builds skip the test as timing-sensitive.

State and persistence: Mutates the global ratelimiter tables, GC state, total entry count, and init refcount during testing, then clears them. No intended persistent state remains.

Dependencies and integration points: Included by `ratelimiter.c` in DEBUG builds and invoked from `main.c`. Uses internal ratelimiter globals and functions, jiffies, msleep, IPv4/IPv6 headers, and init_net.

Risks: Timing tests are disabled unless `DEBUG_RATELIMITER_TIMINGS` because scheduler delays can cause false failures. Capacity test can be expensive on large tables. It does not simulate real handshake/cookie integration.

Test signals: DEBUG module load should print ratelimiter self-tests pass; failures indicate init refcount, token bucket, IPv4/IPv6 keying, GC cleanup, or max-entry regressions.
