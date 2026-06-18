# sources/distributed-fs/ceph-client/drivers/scsi/snic/snic_trc.h

Purpose: this header defines SNIC trace data structures, trace APIs, and trace macros for debugfs and non-debug builds.

Important APIs, types, and functions: under `CONFIG_SCSI_SNIC_DEBUG_FS`, `struct snic_trc_data` defines a packed 64-byte trace record with timestamp, function pointer, host number, tag, and five data fields; `struct snic_trc` defines the ring buffer. It declares trace/debugfs lifecycle APIs and defines `snic_trace()` plus `SNIC_TRC()`. Without debugfs, `SNIC_TRC()` falls back to conditional printk-style logging. `SNIC_TRC_CMD()` and `SNIC_TRC_CMD_STATE_FLAGS()` compact SCSI command and state data into integers.

Control flow: SCSI queueing, completion, abort, reset, and cleanup paths invoke `SNIC_TRC()`. In debugfs builds records are appended to the ring; otherwise output depends on `snic_log_level`.

State and persistence: trace state exists only when debugfs is enabled and is stored in `snic_glob->trc`. There is no persistent trace storage.

Dependencies and integration: depends on `snic_glob`, `snic_log_level`, command-state macros from `snic.h`, and debugfs implementation in `snic_trc.c`/`snic_debugfs.c`.

Risks: macros evaluate command fields directly, so callers must only pass valid `scsi_cmnd` pointers. The non-debug fallback emits logs from hot paths when logging bit 0x2 is set. Trace entry size is fixed at 64 bytes and must match structure layout.

Test signals: compile both debugfs and non-debug variants, verify trace entries include expected command tags/states, and test ring wrap/read behavior.
