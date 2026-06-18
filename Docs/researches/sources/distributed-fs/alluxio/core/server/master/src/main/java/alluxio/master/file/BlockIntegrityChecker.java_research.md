# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/BlockIntegrityChecker.java

## Purpose
`BlockIntegrityChecker` is a heartbeat executor that periodically asks the file-system master to validate inode-to-block metadata consistency and optionally repair invalid blocks.

## Important APIs and Types
- Implements `HeartbeatExecutor`.
- Constructor stores `FileSystemMaster` and reads `MASTER_PERIODIC_BLOCK_INTEGRITY_CHECK_REPAIR`.
- `heartbeat(long)` calls `mFileSystemMaster.validateInodeBlocks(mRepair)`.
- `close()` is a no-op.

## Control Flow
On each heartbeat tick, the checker delegates the full validation/repair decision to `FileSystemMaster`. Any exception is caught and logged so the heartbeat thread continues running.

## State and Persistence Behavior
The checker has no persistent state. Repair behavior, when enabled, is performed by the file/block master methods reached through `validateInodeBlocks`.

## Dependencies and Integration Points
It depends on heartbeat infrastructure, `FileSystemMaster`, Alluxio configuration, and logging. It is scheduled by file master startup code for periodic integrity checking.

## Risks and Edge Cases
Catching all exceptions prevents heartbeat death but can hide repeated failures except in logs. `timeLimitMs` is ignored, so a long validation can exceed heartbeat budget. The repair flag is read once at construction and does not reflect later config changes.

## Test Signals
Periodic validation is usually covered through file-system master integrity tests. The search did not show a dedicated `BlockIntegrityCheckerTest`.
