# sources/distributed-fs/ceph-client/include/net/dst_cache.h

Read `sources/distributed-fs/ceph-client/include/net/dst_cache.h` completely for this pass (109 lines, 3043 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/dst_cache.h_research.md`.

Purpose: declares a per-CPU destination cache used by tunnels and similar paths to cache route lookups plus source addresses without global contention.

Important APIs/types/functions: `struct dst_cache` stores a per-CPU `dst_cache_pcpu` pointer and a `reset_ts` invalidation timestamp. APIs include `dst_cache_get()`, `dst_cache_get_ip4()`, `dst_cache_set_ip4()`, optional IPv6 `dst_cache_set_ip6()` and `dst_cache_get_ip6()`, `dst_cache_reset()`, `dst_cache_reset_now()`, `dst_cache_init()`, and `dst_cache_destroy()`.

Control flow: a caller initializes the cache, disables local BH, attempts a per-CPU `dst_cache_get*()`, performs a route lookup on miss, then stores the result with `dst_cache_set*()`. `dst_cache_reset()` lazily invalidates entries by updating `reset_ts`; the next per-CPU access drops stale dsts. `dst_cache_reset_now()` frees entries immediately when the caller guarantees no concurrent users.

State and persistence: per-CPU cache entries hold dst references and optional IPv4/IPv6 source addresses. `reset_ts` provides lazy global invalidation. State is runtime only and must be destroyed on owner teardown.

Dependencies and integration points: depends on jiffies, dst entries, IPv4 rtables, optional IPv6 fib types, local BH discipline, and tunnel metadata (`ip_tunnel_info` embeds a dst cache).

Risks: callers must disable local BH around get/set. Immediate reset/destroy require no concurrent users. Forgetting destroy leaks dst references/per-CPU memory. IPv6 APIs are config gated. Cached dsts must be invalidated when route-affecting metadata changes.

Test signals: cache hit/miss for IPv4 and IPv6, local-BH assertions or lockdep coverage, lazy reset freeing on next access, immediate reset with no users, destroy leak checks, route change invalidation, and tunnel transmit performance/regression tests.
