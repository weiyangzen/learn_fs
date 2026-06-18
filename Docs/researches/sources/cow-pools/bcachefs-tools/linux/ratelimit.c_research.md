# File Research: sources/cow-pools/bcachefs-tools/linux/ratelimit.c

Implements `___ratelimit()` for `struct ratelimit_state`. It enforces interval/burst limits, handles uninitialized and disabled states, uses raw spin trylock plus atomic remaining-burst counters, reports suppressed callbacks when appropriate, and increments miss counters on suppression.

This mirrors kernel printk-style rate limiting for userspace diagnostics.
