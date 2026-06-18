# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_stats.h

Purpose: this header defines SNIC driver statistics structures and small inline update helpers.

Important APIs, types, and functions: `struct snic_io_stats`, `snic_abort_stats`, `snic_reset_stats`, `snic_fw_stats`, `snic_misc_stats`, and aggregate `struct snic_stats` hold atomic counters for active/completed/failed I/O, SG distribution, abort/reset outcomes, firmware errors, ISR activity, queue depth changes, and miscellaneous conditions. `snic_stats_update_active_ios()` updates maximum active I/O and total I/O count. `snic_stats_update_io_cmpl()` decrements active I/O and increments completion unless a reset skip counter is active.

Control flow: queueing, completion, abort, reset, ISR, debugfs reset, and cleanup paths update these counters. Debugfs reads format them for operators.

State and persistence: stats are per-adapter runtime atomic counters in `snic->s_stats`, plus an `io_cmpl_skip` used to reconcile stats after reset. They are not persisted and can be reset via debugfs when enabled.

Dependencies and integration: declarations for debugfs init/remove are implemented only in the debugfs build. The header relies on `SNIC_MAX_SG_DESC_CNT` being defined by included context before use.

Risks: stats are advisory and can be approximate under concurrency, especially max counters updated with read-then-set rather than compare/exchange. Resetting stats while I/O is active uses skip logic but can still produce transiently surprising values.

Test signals: debugfs stats under sustained I/O, aborts, firmware errors, queue full, and resets should move expected counters. Race testing should check for negative active counts or completion mismatches.
