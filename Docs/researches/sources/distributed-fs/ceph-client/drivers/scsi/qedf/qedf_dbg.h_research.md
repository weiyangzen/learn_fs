# sources/distributed-fs/ceph-client/drivers/scsi/qedf/qedf_dbg.h

Purpose: declares QEDF logging categories, debug context, logging macros, GRC/sysfs diagnostic helper APIs, and debugfs operation contracts.

Important APIs/types/functions: log bits include discovery, LL2, connection, events, timers, middle path, SCSI task management, unsolicited frames, I/O, multiqueue, BSG, debugfs, lport, ELS, NPIV, session, TID tracking, notices, and warnings. `struct qedf_dbg_ctx` carries host number, PCI device, and optional debugfs dentry. `QEDF_ERR`, `QEDF_WARN`, `QEDF_NOTICE`, and `QEDF_INFO` inject `__func__` and `__LINE__` into the logging helpers. `struct sysfs_bin_attrs` describes binary sysfs files. `struct qedf_debugfs_ops`, `struct qedf_list_of_funcs`, and the `qedf_dbg_fileops*` macros define the debugfs file table and file-operation boilerplate. It declares lifecycle hooks `qedf_dbg_host_init()`, `qedf_dbg_host_exit()`, `qedf_dbg_init()`, and `qedf_dbg_exit()` under `CONFIG_DEBUG_FS`.

Control flow: this header provides macros and declarations only. Runtime users call the macros; `qedf_dbg.c` performs log filtering and printing, while `qedf_debugfs.c` consumes the debugfs operation arrays to create per-host files.

State and persistence: the global `qedf_debug` bitmask controls logging at runtime. `qedf_dbg_ctx::bdf_dentry` persists for the lifetime of a debugfs host directory when debugfs is enabled. No on-disk persistence exists.

Dependencies and integration: includes kernel types, PCI, fs/debug support, SCSI transport, and QED common interfaces. The header is included from `qedf.h`, so these diagnostic contracts are visible across the driver. Debugfs declarations are compiled conditionally, but stub prototypes are still provided by `qedf_debugfs.c` when disabled.

Risks and test signals: because log categories are bitmasks used across many files, collisions or incorrect defaults can make diagnostics noisy or silent. The `QEDF_TRACK_CMD_LIST` value overlaps tracking bits intentionally and should not be treated as an independent single bit. Function signatures must stay aligned with `qedf_dbg.c` and debugfs file tables. Build tests with and without `CONFIG_DEBUG_FS`, plus runtime checks of log mask writes and debugfs host creation/removal, are the key signals.
