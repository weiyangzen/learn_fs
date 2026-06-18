# File Research: sources/cow-pools/bcachefs-tools/include/linux/printk.h

This header provides kernel printk-style logging APIs. It defines kernel log-level prefixes, `vscnprintf()`, `scnprintf()`, `vprintk()`, `printk()`, `no_printk()`, `pr_emerg()` through `pr_debug()`, one-shot logging macros, and ratelimited logging macros.

`pr_devel`/`pr_debug` compile away unless debugging is enabled. One-shot macros use a static boolean. Ratelimited macros instantiate a local `ratelimit_state` and call `__ratelimit()` before printing. `dump_stack()` is declared externally.
