# sources/distributed-fs/ceph-client/drivers/ras/debugfs.c

Purpose: provides the shared RAS debugfs root and a lightweight userspace-consumer signal. Other RAS components use this root for their own debugfs directories, and `ras_userspace_consumers()` reports whether the daemon trace file is open.

Important APIs and functions: `ras_get_debugfs_root()` returns the global root dentry. `ras_userspace_consumers()` returns `trace_count`. `ras_debugfs_init()` creates the top-level `ras` directory. `ras_add_daemon_trace()` creates the `daemon_active` file. `trace_open()` increments and `trace_release()` decrements the atomic count around a trivial `single_open()` file.

Control flow: `ras_init()` in `ras.c` calls `ras_debugfs_init()` before `ras_add_daemon_trace()`. Consumers such as CEC and FMPM call `ras_get_debugfs_root()` and skip debugfs setup if it returns NULL. Opening `daemon_active` does not emit content but marks an active userspace consumer until release.

State and persistence: state is process/runtime-only: `ras_debugfs_dir` and atomic `trace_count`. Nothing is persisted. The count is robust to concurrent open/release through atomics.

Dependencies and integration: depends on debugfs, seq_file helpers, and `linux/ras.h`. Exports functions for modules through GPL symbols. The header provides a stub only for the root getter when debugfs is disabled.

Risks: `ras_add_daemon_trace()` only checks `IS_ERR(fentry)` and not NULL, while many debugfs APIs return NULL for disabled or failed creation. A missing root returns `-ENOENT`, causing `ras_init()` to propagate failure. The empty read file is a presence/usage signal, not a data source.

Test signals: boot with debugfs enabled/disabled, verify `/sys/kernel/debug/ras/daemon_active`, concurrent opens and closes updating `ras_userspace_consumers()`, module users seeing NULL root gracefully, and init failure paths.
