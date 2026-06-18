## sources/distributed-fs/ceph-client/lib/ratelimit.c

Purpose: implements the shared `___ratelimit()` helper for limiting repeated callbacks or log messages using a caller-owned `struct ratelimit_state`.

Important API/function: `___ratelimit(struct ratelimit_state *rs, const char *func)` returns 1 when the caller should proceed and 0 when the callback should be suppressed. It is exported as a kernel symbol.

Control flow: the function reads interval and burst with `READ_ONCE()` so concurrent sysctl/proc updates do not create unsafe compiler assumptions. Zero interval disables limiting; nonpositive burst generally suppresses. The hot path tries `raw_spin_trylock_irqsave()`. If contended, it uses atomic `rs_n_left` as an approximate fast path. With the lock held, it initializes the window if needed, resets counts when `begin + interval` has passed, prints suppressed-count messages unless release-reporting is requested, then decrements the remaining burst.

State and persistence: mutable state is entirely in `ratelimit_state`: interval, burst, flags, window start, atomic remaining allowance, and missed count. Misses are incremented when suppressed.

Dependencies/integration: depends on jiffies time helpers, raw spinlocks, atomics, warning infrastructure, and deferred printk.

Risks/test signals: the contended lockless fallback can allow false positives near interval boundaries by design. Negative uninitialized values warn. Test signals are mostly indirect through printk/net ratelimit users and lock/concurrency behavior.
