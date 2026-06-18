# sources/control-plane/longhorn-engine/integration/data/test_restore.py

## Purpose
This module validates Longhorn backup restore behavior, especially disaster-recovery no-frontend volumes, incremental restore chains, restore plus rebuild, expansion-aware restore, and restore failure recovery. It uses real backup targets and intentionally corrupts filesystem or backup-store state to verify restore status semantics.

## Important APIs, types, and functions
- Entry points: `test_restore_with_rebuild`, `test_restore_incrementally`, `test_inc_restore_with_rebuild_and_expansion`, `test_inc_restore_failure_delta_file_cleanup_error`, and `test_inc_restore_failure_invalid_block`.
- Helpers: `restore_inc_test`, `inc_restore_failure_cleanup_error_test`, and `compare_last_restored_with_backup`.
- `common.core` provides volume startup/cleanup, no-frontend DR volume helpers, backup creation/removal, restore polling, frontend expansion, block device checks, and raw no-frontend data verification.
- `common.cmd` provides CLI calls including `backup_restore`, `restore_status`, `backup_inspect`, `backup_volume_list`, `backup_volume_rm`, `snapshot_create`, `snapshot_info`, `snapshot_purge`, `verify_rebuild_replica`, and `sync_agent_server_reset`.
- The test uses `pytest.raises(subprocess.CalledProcessError)` for expected CLI failures and shell tools such as `chattr`, `find`, `mv`, and `rm`.

## Control flow
`test_restore_with_rebuild` creates a backup from a normal frontend volume, restores it to a no-frontend DR volume, adds a second replica with `restore=True`, then triggers a duplicate restore command. The old replica reports already restored, while the rebuilding replica performs full restore and is manually verified before the original replica is removed.

`restore_inc_test` builds five backups with controlled block-level changes. It first forces restore startup failure by marking fixed replica directories immutable and asserts restore status remains clean because failure happened before actual restore. It then restores backup0 through backup4 incrementally, checking data after each restore, last-restored metadata, delta-file cleanup, duplicate restore rejection, fallback to full restore after deleting an intermediate backup, and VFS temporary file cleanup.

The expansion test restores an initial backup, expands the source volume, creates a larger backup, verifies the DR restore rejects larger backups until the DR volume is expanded, handles mandatory snapshot purge before restore, manually expands a rebuilding DR replica, and verifies rebuild restore for the expanded size.

Failure tests simulate delta cleanup failure by pre-creating directory trees where delta files should be removed, and simulate invalid VFS backup blocks by temporarily moving block files out of the backup store while polling restore status for per-replica errors.

## State and persistence behavior
The file tracks backup objects and names, restore status maps, no-frontend replica data, backup volume size metadata, snapshot purge state, delta file presence/absence in fixed replica directories, VFS temporary files, and immutable directory state. It also explicitly resets sync-agent servers and cleans up volumes, replicas, and backups to prevent state leakage between backup targets.

## Dependencies and integration points
Tests integrate the engine controller, no-frontend DR controller, fixed-directory replicas, backupstore backends listed in `backup_targets`, local VFS backup directory constants, snapshot purge, replica rebuild verification, and sync-agent server reset. They require privileged filesystem operations for `chattr` and direct backup-store file mutation.

## Risks and edge cases
- The invalid-block case can wait up to ten minutes to match backupstore retry behavior.
- Tests assume exact CLI error strings such as "already restored backup", "need to expand the DR volume", and "failed to clean up the existing file".
- Direct mutation of backup blocks and immutable attributes can destabilize later tests if cleanup does not run.
- Incremental restore assertions depend on specific delta-file naming conventions based on backup names.
- The expansion path assumes DR rebuilding replicas are not auto-expanded and must be manually expanded before `restore=True` add succeeds.

## Test signals
Primary signals are correct restored bytes in no-frontend replicas, restore status fields (`isRestoring`, `backupURL`, `lastRestored`, `progress`, `state`, `error`), cleanup of obsolete delta/tmp files, fallback to full restore when an incremental base is unavailable, expected failures before status mutation, all replicas returning to `RW`, and expanded backup/volume size metadata.
