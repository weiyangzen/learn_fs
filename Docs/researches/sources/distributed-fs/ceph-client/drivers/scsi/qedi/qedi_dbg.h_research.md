# sources/distributed-fs/ceph-client/drivers/scsi/qedi/qedi_dbg.h

Purpose: this header defines qedi debug masks, logging macros, debug context state, and debugfs operation descriptors.

Important APIs and types: `QEDI_LOG_*` bitmasks cover default, info, discovery, LL2, connection, events, timer, middle-path requests, SCSI task management, unsolicited messages, I/O, multi-queue, BSG, debugfs, lport, ELS, NPIV, session, UIO, TID tracking, command-list tracking, notice, and warning logs. `struct qedi_dbg_ctx` stores `host_no`, `pdev`, and optionally a debugfs dentry. The `QEDI_ERR/WARN/NOTICE/INFO` macros inject `__func__` and `__LINE__`. `struct qedi_list_of_funcs` and `struct qedi_debugfs_ops` describe writable debugfs commands. `qedi_dbg_fileops` and `qedi_dbg_fileops_seq` generate file operation initializers.

Control flow and state: the header declares logging functions implemented in `qedi_dbg.c` and debugfs lifecycle functions implemented in `qedi_debugfs.c` when available. It does not mutate state itself but exposes the global `qedi_dbg_log` mask.

Dependencies and integration points: it includes PCI, SCSI transport, filesystem, and QED common headers, and is included by core qedi files for diagnostics. Debugfs declarations integrate with `qedi_gbl.h` arrays and `qedi_main.c` host init/exit paths.

Risks: debug masks are ABI-like for operators and support tooling. Enabling `QEDI_TRACK_TID` or command-list tracking can be expensive and is documented as load-time-only. Macro misuse with a wrong context pointer can degrade logs or crash if the pointer is invalid despite the implementation's null checks.

Test signals: compile with and without `CONFIG_DEBUG_FS`, verify logging macro expansion, toggle module debug masks, create and remove per-host debugfs entries, and inspect that warning/notice high-bit masks do not collide with lower functional masks unexpectedly.
