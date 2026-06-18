# sources/distributed-fs/ceph-client/include/linux/ratelimit.h

Purpose: provides helper routines and warning macros around `struct ratelimit_state` for suppressing repeated kernel messages.

Important APIs and types: `ratelimit_state_init()`, `ratelimit_default_init()`, miss counter helpers, `ratelimit_state_reset_interval()`, `ratelimit_state_exit()`, and `ratelimit_set_flags()` manage a ratelimit state. `printk_ratelimit_state` is the global printk state. `WARN_ON_RATELIMIT()` and `WARN_RATELIMIT()` emit warnings only when `__ratelimit()` permits them under `CONFIG_PRINTK`.

Control flow: callers initialize a state with interval/burst, call `__ratelimit()` directly or through macros before emitting messages, count missed events, optionally reset intervals, and report suppressed counts on release if configured.

State and persistence: state is in-memory per ratelimit object: raw spinlock, interval, burst, remaining count, missed count, flags, and begin timestamp.

Dependencies and integration points: depends on ratelimit types, scheduler `current`, spinlocks, atomics, printk/WARN infrastructure, and `___ratelimit()`.

Risks and test signals: risks include using uninitialized states, interval reset races, missing suppressed-line accounting, disabled printk semantic changes, and hot-path overhead. Test burst/interval boundaries, concurrent callers, reset while active, `RATELIMIT_MSG_ON_RELEASE`, disabled interval, and `CONFIG_PRINTK=n` builds.
