# sources/distributed-fs/ceph-client/fs/xfs/xfs_message.c

Purpose: Provides XFS-specific printk, assertion, panic-tag, hex dump, rate-limited buffer alert, and experimental-feature warning helpers. It centralizes message formatting around an optional `struct xfs_mount` so diagnostics include the mounted device id when available.

Important APIs, types, and functions: `xfs_printk_level` formats variadic messages and may emit a stack trace for severe messages when `xfs_error_level` is high. `_xfs_alert_tag` optionally transforms selected alert tags into `BUG()` via `xfs_panic_mask`. `asswarn` and `assfail` implement assertion reporting for warning and fatal modes. `xfs_hex_dump` wraps `print_hex_dump`. `xfs_buf_alert_ratelimited` uses the buffer target I/O error ratelimit state. `xfs_warn_experimental` maps experimental feature ids to one-time mount opstate warnings.

Control flow: Public wrappers build `struct va_format` and call private `__xfs_printk`, which chooses either `XFS (<s_id>)` or plain `XFS` prefixes. Panic-tag alerts test the global panic mask before printing. Experimental warnings use `xfs_should_warn` to set and test per-mount warning bits.

State and persistence behavior: No persistent disk state is modified. Runtime state includes global error/panic tunables and mount opstate warning bits. Assertion helpers can trigger WARN or BUG depending on build and runtime settings.

Dependencies and integration points: Included widely through `xfs_message.h` and `xfs_platform.h`. Uses Linux printk, ratelimit, BUG/WARN, and XFS mount state. The buffer alert helper integrates with `struct xfs_buftarg` error throttling.

Risks: Misclassified log levels could suppress stack traces or over-trigger them. Panic mask behavior is intentionally dangerous for debugging and should not be enabled casually. Callers must avoid passing invalid mount or buffer pointers on error paths.

Test signals: Build in DEBUG, XFS_WARN, and normal modes; verify mount-tagged and unmounted messages; confirm stack traces for high error level severe messages; validate panic-tag conversion under controlled fault injection; check experimental warnings are emitted once per mount state bit; exercise buffer I/O error storms for ratelimit behavior.
