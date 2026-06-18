# sources/distributed-fs/ceph-client/drivers/net/wireguard/ratelimiter.c

Purpose: Implements a global token-bucket ratelimiter for WireGuard handshake initiation packets, keyed by network namespace and source IPv4 address or IPv6 /64.

Important APIs and functions: `wg_ratelimiter_allow()` checks or creates a per-source entry and consumes tokens. `wg_ratelimiter_init()` reference-counts global initialization, creates the entry cache, sizes IPv4/IPv6 hash tables based on RAM, schedules garbage collection, and seeds siphash key. `wg_ratelimiter_uninit()` decrements init refcount, cancels GC, removes all entries, waits for RCU, and frees tables/cache. `wg_ratelimiter_gc_entries()` prunes entries idle for over one second or removes all entries on shutdown. DEBUG builds include `selftest/ratelimiter.c`.

Control flow: On packet check, the code hashes the net namespace pointer and source address into the relevant table. Existing entries update tokens according to elapsed coarse boottime and allow if at least one packet cost is available. Missing entries allocate a new bucket entry up to `max_entries`, initialize it with burst budget minus one packet, and insert under RCU.

State and persistence: Global static state includes kmem cache, siphash key, table lock, init mutex/refcount, total entry count, max entries, table size, delayed GC work, and IPv4/IPv6 hash tables. Entries store last time, tokens, IP, net pointer, spinlock, hlist node, and RCU head.

Dependencies and integration points: Used by WireGuard handshake receive/cookie path to rate-limit unauthenticated initiations. Depends on siphash, coarse boottime, RCU, delayed work, memory sizing, IPv4/IPv6 headers, and DEBUG selftests.

Risks: Global refcounting must match per-device init/uninit. IPv6 intentionally ratelimits by /64, which is security policy. `net_word` truncates the net pointer to 32 bits by design. Table insertion after RCU lookup can race duplicate entries for the same IP under concurrency, affecting strictness but bounded by max entries. GC and shutdown must not free entries still under RCU readers.

Test signals: DEBUG ratelimiter selftest, burst/rate timing behavior, IPv4 and IPv6 /64 keys, max-entry capacity behavior, repeated device create/destroy refcounting, GC expiry, and concurrent handshake flood tests.
