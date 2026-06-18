# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.c

Purpose: this file implements qedi's printk-based logging helpers behind the macros declared in `qedi_dbg.h`.

Important functions: `qedi_dbg_err`, `qedi_dbg_warn`, `qedi_dbg_notice`, and `qedi_dbg_info` format messages with function name, source line, PCI device name, and host number when a valid `qedi_dbg_ctx` is present. Warning, notice, and info logs are gated by the global `qedi_dbg_log` bitmask; errors are always printed.

Control flow and state: each helper builds a `va_format` around a varargs list and emits through `pr_err`, `pr_warn`, `pr_notice`, or `pr_info`. If the context or PCI device is unavailable, it prints a placeholder BDF. The file itself owns no persistent state beyond reading `qedi_dbg_log`.

Dependencies and integration points: all qedi sources use `QEDI_ERR`, `QEDI_WARN`, `QEDI_NOTICE`, and `QEDI_INFO` macros, so this file is central for diagnostics. It depends on kernel varargs formatting and `dev_name(&pdev->dev)`.

Risks: logging is often called in interrupt, atomic, or error paths; format strings and arguments must be safe there. Excessive enabled debug masks can flood kernel logs. Passing user buffers or non-NUL strings to these helpers would be unsafe, but normal use passes driver-controlled formats.

Test signals: compile-time format checking, module parameter changes to `qedi_dbg_log`, verifying that each log level is gated as intended, and exercising logging before PCI context initialization to confirm placeholder output is safe.
