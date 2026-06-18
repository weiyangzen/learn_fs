# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_debugfs.c

Purpose: this optional file creates debugfs directories and files for SNIC statistics and trace output when `CONFIG_SCSI_SNIC_DEBUG_FS` is enabled.

Important APIs, types, and functions: `snic_debugfs_init()` creates `/sys/kernel/debug/snic` and a `statistics` child directory. `snic_stats_debugfs_init()` creates per-host `stats` and `reset_stats` files. `snic_stats_show()` formats I/O, abort, reset, firmware, and miscellaneous counters. `snic_reset_stats_write()` toggles `snic->reset_stats` and zeroes cumulative counters while preserving active counts. Trace helpers create `tracing_enable` and `trace`, with seq operations pulling records from `snic_get_trc_data()`.

Control flow: global debugfs setup happens during SNIC global initialization; per-host setup happens in probe before PCI resource setup and is removed in probe failure/remove. Reading `stats` is a seq-file snapshot of atomic counters. Writing `reset_stats` copies a small user buffer, parses an integer, and resets counters when nonzero. Reading `trace` drains one formatted trace record per seq show call.

State and persistence: state is debugfs dentries in `snic_global` and per `struct snic`, atomic stats in `snic->s_stats`, `snic->reset_stats`, and the trace ring. Debugfs content is runtime-only and disappears when the module unloads.

Dependencies and integration: depends on Linux debugfs, seq-file helpers, SNIC stats definitions, and trace APIs from `snic_trc.c`. It uses `simple_read_from_buffer()` and `copy_from_user()`.

Risks: stats reset uses raw `memset()` over structures containing atomics, which is common in older driver code but deserves care under concurrent updates. Debugfs creation return values are not checked. Trace reads are destructive because `snic_get_trc_data()` advances `rd_idx`.

Test signals: with debugfs enabled, verify directory/file creation and removal across probe/unbind, stats values changing under I/O, reset_stats behavior with valid/invalid writes, and trace enable/disable. Run with CONFIG_DEBUG_ATOMIC_SLEEP and lockdep during concurrent reads and I/O completions.
