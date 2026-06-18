# sources/control-plane/longhorn-engine/integration/core/test_cli.py

## Purpose
Large integration suite validating Longhorn CLI behavior for replica add/rebuild/failure, snapshots, backups, expansion, restart recovery, replica removal/recreation, and mismatched sizes.

## Important APIs, Types, and Functions
- Fixtures: `backup_targets`, `random_str`, session `bin`.
- Helpers: `setup_module`, `getNow`, `backup_core`, local `random_num`.
- Tests include `test_replica_add_start`, `test_replica_add_rebuild`, `test_replica_add_after_rebuild_failed`, `test_replica_failure_detection`, `test_revert`, snapshot CRUD/list/info/purge variants, `test_backup_cli`, expansion tests, restart/failure recovery tests, and `test_replica_with_mismatched_size_add_start`.

## Control Flow
Tests start engines/replicas via fixtures or process managers, open replicas, start volumes, invoke CLI commands via subprocess or `common.cmd`, then assert controller/replica gRPC state, snapshot chain filenames, backup metadata, and output text/JSON. Several tests simulate detach/reattach by deleting processes and recreating them with the same replica dirs. Backup tests manipulate backupstore config files to test corrupt/missing metadata behavior.

## State and Persistence Behavior
Creates real replica disk chains under temp directories, backup metadata under `BACKUP_DIR`, Longhorn frontend devices, and process-manager managed engine/replica processes. It mutates snapshot meta files, kills engine processes, expands volumes, purges snapshots, and removes backup volumes.

## Dependencies and Integration Points
Exercises Go CLI commands in `app/cmd`, generated controller/replica/process-manager clients, `common.core`, `common.cmd`, and backupstore filesystem layout. Backup targets come from `BACKUPTARGETS`.

## Risks and Edge Cases
Tests depend on timing, process cleanup, privileged environment, and exact CLI output formatting. Some retry loops are bounded but may be flaky on slow systems. Direct backup metadata corruption/removal assumes backupstore file layout. `test_expand_multiple_times` repeatedly creates clients/processes and can be expensive.

## Test Signals
Provides strong end-to-end signal for command-layer behavior: snapshot listing format, backup JSON contracts, rebuild completion, purge semantics, expansion snapshot handling, restart recovery after SIGKILL, and replica mode transitions.
