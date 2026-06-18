# sources/distributed-fs/ceph-client/include/linux/dev_printk.h

Purpose: Defines device-scoped printk helpers that attach subsystem/device identity to kernel logs and provide once, ratelimited, dynamic-debug, WARN, and probe-error variants.

Important APIs, types, and functions: Defines `struct dev_printk_info`, `dev_vprintk_emit()`, `dev_printk_emit()`, `_dev_printk()` and level-specific `_dev_*()` functions when printk is enabled. Macros include `dev_printk()`, `dev_no_printk()`, `dev_emerg/alert/crit/err/warn/notice/info/dbg`, once and ratelimited variants, `dev_vdbg`, `dev_WARN`, `dev_WARN_ONCE`, `dev_err_probe()`, `dev_warn_probe()`, `dev_err_ptr_probe()`, and `dev_err_cast_probe()`.

Control flow: Device log macros emit printk index metadata, apply `dev_fmt()`, and call level-specific emitters. `dev_dbg()` routes through dynamic debug, unconditional debug, or compile-time checked no-op depending on configuration. Once macros use static booleans; ratelimited macros use static ratelimit state. Probe helpers normalize deferred-probe logging and return the original error for convenient propagation.

State and persistence: Log state includes static once flags, ratelimit buckets, dynamic-debug descriptors, and emitted printk records. No driver state is persisted.

Dependencies and integration points: Depends on printk, dynamic debug, ratelimit, WARN, `dev_name()`, and `dev_driver_string()` from the driver core. Integrated across nearly all device drivers for diagnostics.

Risks and test signals: Risks include format-string mistakes, log flooding when ratelimit is bypassed, missing output with `CONFIG_PRINTK=n`, dereferencing invalid `struct device`, and noisy deferred-probe logs. Test compile-time format checking, dynamic debug enablement, ratelimited suppression, once-only output, probe deferral paths, and no-printk builds.
