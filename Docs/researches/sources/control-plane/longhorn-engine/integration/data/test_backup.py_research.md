# sources/control-plane/longhorn-engine/integration/data/test_backup.py

## Purpose
Comprehensive data-path backup integration suite covering backup/restore integrity, backing-file volumes, sparse holes, snapshot trees, incremental/full backup decisions, block deletion/GC, corrupt metadata, volume deletion/listing, backup locks, and backup type behavior.

## Important APIs, Types, and Functions
- Helpers: `backup_test`, `backup_with_backing_file_test`, `backup_hole_with_backing_file_test`, `snapshot_tree_backup_test`, `check_backup_volume_block_count`, lock helpers.
- Tests: `test_backup`, `test_backup_S3_latest_unavailable`, `test_backup_incremental_logic`, `test_snapshot_tree_backup`, backing-file qcow2/raw tests, block deletion/no-cleanup/corrupt deletion, volume deletion/list, `test_backup_lock`, and `test_backup_type`.
- Constants: lock names/types, backing image name/checksum.

## Control Flow
Tests create volumes, write random data, snapshot, create backups, inspect metadata, reset volumes, restore backups, and verify exact data/checksums. Several tests directly edit backupstore files: remove cfgs, corrupt cfg JSON, create in-progress backup cfgs, add bad filenames, remove volume.cfg, count `.blk` files, and create lock files. Lock tests assert operations fail while conflicting locks are acquired and succeed after removal.

## State and Persistence Behavior
Heavily mutates Longhorn volumes, backupstore filesystem under `BACKUP_DIR`, replica state, frontend state, and backup locks. It verifies persistent data by whole-device checksum and targeted reads. It also validates garbage collection of backup blocks and preservation when in-progress backup metadata exists.

## Dependencies and Integration Points
Uses `common.cmd`, `common.core`, `data.snapshot_tree`, constants, `common.util.finddir/findfile`, pytest, subprocess, JSON, pathlib. Exercises Go backup/snapshot/restore command surfaces and backupstore layout.

## Risks and Edge Cases
Tests assume backupstore on local filesystem even for S3-oriented cases enough to inspect `BACKUP_DIR`. Direct metadata manipulation is brittle to backupstore layout changes. Lock timeout tests depend on lock refresh/max wait constants and subprocess failures. Whole-device checksums on small test volumes are sensitive to expected zeroing semantics.

## Test Signals
Very strong signal for backup correctness: incremental vs full selection, backing image metadata, sparse holes, block deduplication/deletion, corrupt/missing metadata handling, lock conflict behavior, volume list resilience, and data restoration from branchy snapshots.
