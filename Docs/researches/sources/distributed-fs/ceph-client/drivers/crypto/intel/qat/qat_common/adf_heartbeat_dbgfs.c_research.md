# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_common/adf_heartbeat_dbgfs.c

Purpose: exposes heartbeat status, statistics, runtime timer configuration, and optional error injection through debugfs under each QAT device.

Important APIs: `adf_heartbeat_dbgfs_add` creates `heartbeat/status`, `queries_sent`, `queries_failed`, `config`, and optionally `inject_error`. `adf_heartbeat_dbgfs_rm` removes those dentries. File operations implement reads for counters/status/config, writes for config, and writes for injection.

Control flow and state: reading `status` invokes `adf_heartbeat_status`, so it can update counters and trigger reset notification on failures. Writing `config` validates integer input, enforces minimum timer, pins timer to 200 ms when `accel_dev->timer` exists, persists config, converts to ticks, and sends an admin timer command. Error injection accepts only a single `1\n` style write.

Dependencies and integration: depends on debugfs, admin heartbeat timer command, config storage, and `adf_heartbeat_inject_error`.

Risks and test signals: status reads have side effects; config writes race with active polling only through heartbeat fields without a local lock. Test valid/invalid config writes, min timer enforcement, debugfs removal during device stop, and injected failure propagation.
