<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dfs.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dfs.c

## Purpose

`qla_dfs.c` implements the qla2xxx driver's debugfs interface. It exposes per-adapter diagnostics under a shared `qla2xxx` debugfs root, per-remote-port state under each host's `rports` directory, firmware resource counts, target counters, target session and port-database snapshots, FCE trace control/dump access, and a target multi-queue `naqp` knob on supported adapters.

This file is diagnostic and control-plane oriented. It does not submit normal SCSI I/O, but it can issue mailbox commands, pause and re-enable firmware event tracing, alter target queue-pair selection, and change NVMe remote-port `dev_loss_tmo`.

## Important APIs, Types, And Functions

- `qla2x00_dfs_setup()` creates the global debugfs root once, creates the per-HBA directory named by `vha->host_str`, initializes `ha->fce_mutex`, and installs files such as `fw_resource_count`, `tgt_counters`, `tgt_port_database`, `fce`, `tgt_sess`, optional `naqp`, and `rports`.
- `qla2x00_dfs_remove()` removes all per-host files, recursively removes `vha->dfs_rport_root`, decrements `qla2x00_dfs_root_count`, and removes the global root when the last host leaves.
- `qla2x00_dfs_create_rport()` and `qla2x00_dfs_remove_rport()` maintain per-`fc_port` directories named `pn-%016llx`, with read-only state files and an NVMe-only read/write `dev_loss_tmo`.
- `qla_dfs_rport_get()`/`qla_dfs_rport_set()` implement the only writable rport attribute, guarding it with `NVME_FLAG_REGISTERED` and `CONFIG_NVME_FC`.
- `qla2x00_dfs_tgt_sess_show()`, `qla2x00_dfs_tgt_port_database_show()`, `qla_dfs_fw_resource_cnt_show()`, and `qla_dfs_tgt_counters_show()` are `seq_file` producers for target/session, name-list, firmware resource, and aggregate counter data.
- `qla2x00_dfs_fce_open()`, `qla2x00_dfs_fce_show()`, `qla2x00_dfs_fce_write()`, and `qla2x00_dfs_fce_release()` form a custom `file_operations` implementation for Fibre Channel event tracing.
- `qla_dfs_naqp_show()`/`qla_dfs_naqp_write()` expose and alter `ha->tgt.num_act_qpairs` for selected multi-queue capable adapters.

## Control Flow

Probe or host setup calls `qla2x00_dfs_setup()`. Unsupported adapter families return without creating entries. Supported families create the root if needed, the host directory if absent, then unconditionally create the normal diagnostic files. Each remote `fc_port` can later call `qla2x00_dfs_create_rport()` once its host has an `rports` root; removal mirrors this path and nulls the stored dentries.

Most reads are direct snapshots. Target sessions are printed while holding `ha->tgt.sess_lock`. Target port database output allocates a coherent GID-list buffer, waits for `qla24xx_gidlist_wait()`, and prints each firmware loop ID through `qla24xx_print_fc_port_id()`. Firmware resource counts call `qla24xx_res_count_wait()` and optionally add driver-side IOCB/exchange usage across queue pairs. Target counters aggregate `qpair->tgt_counters`, DIF stats, host error counters, and per-rport link-down counters.

The `fce` node has active side effects. Opening it disables FCE tracing when currently enabled so the buffer can be read consistently. Releasing it reinitializes and re-enables tracing if the buffer still exists. Writing a non-zero value allocates FCE buffers if needed, adjusts firmware dump allocation, marks `user_enabled_fce`, and enables tracing. Writing zero disables tracing and frees the FCE trace buffer.

The `naqp` write path validates adapter family, multi-queue availability, and the requested count against `ha->max_qpairs`; a change updates `ha->tgt.num_act_qpairs` and clears the target queue-pair table.

## State And Persistence Behavior

The file persists only debugfs dentries and driver diagnostic state. Global state is `qla2x00_dfs_root` plus `qla2x00_dfs_root_count`; per-HBA state lives in `ha->dfs_*`, `ha->tgt.dfs_*`, `vha->dfs_rport_root`, and each `fc_port->dfs_rport_dir`. Removing nodes sets these pointers back to `NULL`.

FCE state changes are persistent driver/runtime changes until explicitly changed, adapter reset, or host removal: `ha->flags.user_enabled_fce`, `ha->flags.fce_enabled`, `ha->fce`, `ha->fce_dma`, `ha->fce_mb`, and `ha->fce_bufs` are modified under `ha->fce_mutex`. `dev_loss_tmo` writes persist in the NVMe FC remote-port object. `naqp` writes persist in `ha->tgt.num_act_qpairs` until changed or the adapter is reinitialized.

## Dependencies And Integration Points

The file depends on `qla_def.h`, debugfs, `seq_file`, NVMe FC remote-port helpers, target-mode structures, qla mailbox helpers, qpair accounting, and firmware trace helpers declared elsewhere. It integrates with `qla_gbl.h` through exported prototypes for debugfs setup/removal and rport directory creation/removal. It also relies on target-mode support functions such as `qlt_clr_qp_table()` and firmware helpers such as `qla24xx_res_count_wait()`.

## Risks And Edge Cases

- Debugfs creation is mostly best-effort. Several `debugfs_create_file()` results are stored without `IS_ERR()` handling; cleanup tolerates `NULL` but not every failed dentry path reports an error.
- `qla2x00_dfs_setup()` can recreate files on repeated calls if `ha->dfs_dir` already exists but individual file pointers are not checked first.
- `qla_dfs_fw_resource_cnt_show()` intentionally reads IOCB/exchange counters without locking, so its driver-side usage values are estimates.
- `qla_dfs_naqp_write()` uses `simple_strtoul()` and creates `naqp` with mode `0400` despite wiring a write handler, making writability dependent on debugfs mode behavior and worth checking.
- FCE open/release changes firmware tracing around a read. Concurrent writes, host teardown, or firmware reset paths must respect `ha->fce_mutex` and buffer lifetime.
- Per-rport debugfs fields read live `fc_port` members with minimal locking. They are diagnostic snapshots and can race with discovery/session teardown unless callers remove rport directories before freeing `fc_port`.

## Test Signals

Useful tests include building with `CONFIG_DEBUG_FS`, `CONFIG_NVME_FC`, target mode, and EDIF/FCE-capable adapter support enabled. Runtime validation should confirm debugfs tree creation/removal across multiple HBAs, per-rport directory lifetime during discovery and deletion, successful and rejected `dev_loss_tmo` writes for registered and unregistered NVMe ports, FCE enable/read/disable flows, firmware resource count reads during I/O, and `naqp` validation on supported and unsupported hardware. Teardown tests should verify that no stale debugfs dentries remain after host removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_dfs.c -->
