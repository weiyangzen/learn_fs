# File Research: sources/cow-pools/bcachefs-tools/include/linux/ratelimit.h

This header defines Linux ratelimit state and helpers. `struct ratelimit_state` contains a raw spinlock, interval, burst, remaining count, missed count, flags, and window start. Default interval is `5 * HZ`, burst is `10`.

It provides state initializers, `DEFINE_RATELIMIT_STATE`, `__ratelimit()`, initialization/reset helpers, missed-line accounting, release reporting, flag setting, and warning macros. When `CONFIG_PRINTK` is absent, ratelimited warning macros fall back to normal `WARN` behavior.
