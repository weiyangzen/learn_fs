# sources/control-plane/longhorn-engine/integration/common/cmd.py

## Purpose
Provides Python subprocess wrappers around the Longhorn CLI for integration tests, normalizing binary path, command construction, JSON parsing, retries, and simple assertions.

## Important APIs, Types, and Functions
- `_bin()` resolves `integration/bin/longhorn`.
- Volume/snapshot wrappers: `info_get`, `snapshot_create`, `snapshot_rm`, `snapshot_revert`, `snapshot_ls`, `snapshot_info`, `snapshot_purge`, `snapshot_purge_status`.
- Backup wrappers: `backup_create`, `backup_status`, `backup_restore`, `backup_inspect_volume`, `backup_inspect`, `backup_volume_rm`, `backup_volume_list`, `restore_status`, `restore_to_file`.
- Replica/rebuild wrappers: `add_replica`, `replica_rebuild_status`, `verify_rebuild_replica`, `sync_agent_server_reset`, `set_unmap_mark_snap_chain_removed`.

## Control Flow
Each helper builds an argv list and calls `subprocess.check_output` or `check_call`. JSON-producing commands are parsed immediately. `backup_create` asserts fields in returned create info, then polls `backup_status` until complete/error or retry exhaustion.

## State and Persistence Behavior
Mutates test volumes through CLI commands: snapshots, backups, restores, replica additions, sync-agent reset, and controller flags. It also observes backup metadata and volume state.

## Dependencies and Integration Points
Central bridge between Go CLI command files and Python tests. Depends on `RETRY_COUNTS`, `RETRY_INTERVAL`, and `SIZE` constants. Many tests import as `common.cmd`.

## Risks and Edge Cases
Helpers assert expected response fields, so CLI output schema changes break tests early. Some functions accept labels as dict but `create_backup` in `common.core` passes `[]`, which makes `backup_create` iterate zero keys. Retry exhaustion in `backup_status` returns empty output rather than explicitly failing unless callers assert later.

## Test Signals
All CLI-oriented integration tests use this file, giving strong signal for command syntax and JSON contracts.
