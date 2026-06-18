# sources/control-plane/longhorn-engine/integration/common/core.py

## Purpose
Provides the main integration-test harness for process lifecycle, controller/replica setup, cleanup, retry polling, block device IO verification, backup/snapshot helpers, volume expansion, checksum utilities, and host namespace filesystem interactions.

## Important APIs, Types, and Functions
- Process lifecycle: `cleanup_process`, `wait_for_process_running`, `wait_for_process_error`, `create_replica_process`, `create_engine_process`, `delete_process`, `wait_for_process_deletion`, `upgrade_engine`.
- Controller/replica cleanup and access: `cleanup_controller`, `cleanup_replica`, `get_replica`, `get_controller_version_detail`.
- Volume/test data helpers: `reset_volume`, `get_dev`, `get_blockdev`, `write_dev`, `read_dev`, `verify_data`, `verify_read`, `verify_async`.
- Backup/snapshot helpers: `create_backup`, `rm_backups`, `rm_snaps`, `snapshot_revert_with_frontend`, `restore_with_frontend`, `wait_for_purge_completion`, `wait_for_restore_completion`, `wait_for_rebuild_complete`.
- Expansion and filesystem helpers: `expand_volume_with_frontend`, `wait_for_volume_expansion`, `check_block_device_size`, `get_nsenter_cmd`, `checksum_filesystem_file`, `write_filesystem_file`, `remove_filesystem_file`.
- Data models: `Data` and `Snapshot`.

## Control Flow
Most helpers wrap eventual consistency with retry loops and assertions. Process helpers create processes through instance-manager RPCs and poll state. Cleanup shuts down controllers, deletes replicas, waits for iSCSI session cleanup, then removes process-manager entries. Data helpers write/read through block devices, calculate whole-device checksums, and coordinate frontend shutdown around restore/revert/expansion operations.

## State and Persistence Behavior
Actively mutates process-manager process state, replica directories, block devices, backup directories, Longhorn frontend devices, and host filesystem files. It performs cleanup of backend files and replica directories and resets volumes repeatedly to isolate tests.

## Dependencies and Integration Points
Imports generated controller and process-manager clients, `common.cmd`, `common.frontend`, `common.util`, constants, grpc, pytest, subprocess, tempfile, fcntl/ioctl, and threading. It is the central dependency for core and data integration suites.

## Risks and Edge Cases
Many helpers use asserts for control flow, making failures immediate but sometimes low-context. Race workarounds use sleeps. Global `thread_failed` must be reset after async verifier failures. Cleanup includes shell `rm -r dir + "*"`, process-manager deletion retries, and host namespace commands that require privileged environment.

## Test Signals
This file is test infrastructure rather than tests. Its behavior is transitively validated by all integration suites; failures here often indicate environment, process lifecycle, or eventual-consistency assumptions.
