<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.c -->
# sources/distributed-fs/ceph-client/drivers/md/dm-audit.c

## Purpose
`dm-audit.c` creates Linux audit records for Device Mapper control operations and I/O-related target events.

## Important APIs, Types, And Functions
`dm_audit_log_start()` checks `audit_enabled`, starts an audit buffer, and writes `module` and `op`. `dm_audit_log_ti()` logs target-instance events for `AUDIT_DM_CTRL` and `AUDIT_DM_EVENT`, deriving mapped-device major/minor numbers from `dm_table_get_md()` and `dm_disk()`. `dm_audit_log_bio()` logs bio events using `bio->bi_bdev`, sector, and result. Public functions are GPL-exported.

## Control Flow
Callers pass prefix, operation, target or bio, and result. Disabled audit or allocation failure skips logging. Control events include task info and success/error message; event logs include device and sector. Successful paths append `res` and end the record.

## State And Persistence
No DM metadata is persisted. Audit records are emitted to the external kernel audit subsystem.

## Dependencies, Integration Points, Risks, And Test Signals
It depends on Linux audit APIs, DM core, block/bio helpers, and audit constants. Risks include silent no-op for unexpected audit types, result-convention mismatch in `error_msg`, and bio device/sector ambiguity after remapping. Test enabled/disabled builds, audit on/off, allocation failure, success/error logs, bio events, and field formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/dm-audit.c -->
