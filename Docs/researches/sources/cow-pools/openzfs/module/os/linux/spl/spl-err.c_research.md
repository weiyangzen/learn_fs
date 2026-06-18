# File Research: sources/cow-pools/openzfs/module/os/linux/spl/spl-err.c

Read completely: 124 lines.

This implements Solaris-style SPL error reporting and panic helpers on Linux.

Key responsibilities:
- Provides `spl_dumpstack()`, `spl_panic()`, `vcmn_err()`, and `cmn_err()`.
- Exposes `spl_panic_halt`, which controls whether assertion/panic paths call Linux `panic()` or only log, dump stack, and park the thread.

Important implementation details:
- `spl_panic()` strips the source filename basename, formats the panic message, logs it at emergency priority, optionally calls `panic()`, dumps the stack, then sets the current task uninterruptible and schedules forever.
- `vcmn_err()` maps `CE_IGNORE`, `CE_CONT`, `CE_NOTE`, `CE_WARN`, and `CE_PANIC` to Linux printk levels and the same optional-halt behavior.
- `cmn_err()` is a varargs wrapper around `vcmn_err()`.

Dependencies and interactions:
- Used by SPL assertion/error macros and exported for other OpenZFS modules.
- Integrates with Linux printk, `dump_stack()`, scheduler state, and module parameter handling.

Reliability notes:
- When `spl_panic_halt=0`, panic paths intentionally immobilize only the current thread for debugging instead of crashing the node.
