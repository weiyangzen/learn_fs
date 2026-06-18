# sources/distributed-fs/ceph-client/net/core/dst_cache.c

Purpose: Per-CPU cache for `dst_entry` pointers and associated source addresses. It lets tunnel and routing users cache a validated destination per CPU while supporting global reset and IPv4/IPv6 source-address retrieval.

Important APIs, types, and functions: `struct dst_cache_pcpu` stores refresh timestamp, cached dst, local BH lock, protocol cookie, and either IPv4 or IPv6 source address. Exports include `dst_cache_get()`, `dst_cache_get_ip4()`, `dst_cache_set_ip4()`, `dst_cache_set_ip6()`, `dst_cache_get_ip6()`, `dst_cache_init()`, `dst_cache_destroy()`, and `dst_cache_reset_now()`.

Control flow and state: Set paths take the current CPU's `local_lock_nested_bh()`, release any old cached dst, hold the new dst, store validation cookie, and save source address. Get paths take the same local lock, hold the cached dst for the caller, then validate it against `reset_ts`, `dst->obsolete`, and protocol `ops->check()` using the stored cookie. Invalid entries are cleared and released. `dst_cache_reset_now()` advances the global reset timestamp and clears all per-CPU dsts immediately.

Dependencies and integration points: The file depends on percpu allocation, local locks, softirq context expectations, IPv4 route tables, optional IPv6 fib cookies, and dst reference helpers. It is used by metadata tunnel destinations and tunnel protocols that repeatedly resolve similar routes.

Risks: Helpers warn if used outside softirq context for per-CPU dst manipulation. Missing dst holds or releases would leak routes or return freed routes. `reset_ts` validation is timestamp based, so callers that require immediate invalidation must use `dst_cache_reset_now()`. IPv6 correctness depends on storing and checking route cookies from `rt6_get_cookie()`.

Test signals: Validate cache hit/miss behavior per CPU, reset invalidation, obsolete dst `ops->check()` failure, IPv4 and IPv6 source-address return, destroy releasing all per-CPU references, and lockdep-clean use from BH/softirq contexts.
