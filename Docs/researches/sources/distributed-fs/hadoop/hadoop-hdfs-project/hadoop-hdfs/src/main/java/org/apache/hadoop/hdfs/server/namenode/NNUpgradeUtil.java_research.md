# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/NNUpgradeUtil.java

## Purpose
`NNUpgradeUtil` is a static helper for NameNode storage directory upgrade lifecycle operations: pre-upgrade staging, upgrade completion, finalize, rollback capability checks, and rollback execution.

## Important APIs and Types
- `canRollBack(StorageDirectory, StorageInfo, StorageInfo, int)` validates whether a `previous` directory can roll back to a target layout version.
- `doPreUpgrade(Configuration, StorageDirectory)` renames `current` to `previous.tmp`, creates a new `current`, and hard-links existing edit log files into it.
- `renameCurToTmp(StorageDirectory)` performs the invariant-checked `current` to `previous.tmp` transition.
- `doUpgrade(StorageDirectory, Storage)` writes new VERSION properties and promotes `previous.tmp` to `previous`.
- `doFinalize(StorageDirectory)` removes the rollback snapshot by renaming `previous` to `finalized.tmp` and deleting it.
- `doRollBack(StorageDirectory)` removes current state and restores `previous` as `current`.

## Control Flow
Pre-upgrade requires `current` to exist and both `previous` and `previous.tmp` not to exist. It renames current to tmp, recreates current, and walks one directory level of tmp without following links; regular files whose names start with `edits` are hard-linked into the new current dir so edits survive the transition. Upgrade then writes VERSION metadata into current and renames previous.tmp to previous. Finalize checks for `previous`, renames it to a temporary finalized directory, and deletes it. Rollback renames current to removed.tmp, renames previous to current, then deletes removed.tmp.

## State and Persistence Behavior
All behavior is persistent filesystem mutation on `StorageDirectory` roots. The directory names `current`, `previous`, `previous.tmp`, `removed.tmp`, and `finalized.tmp` are the state machine. VERSION files are written during `doUpgrade`; `canRollBack` reads both current and previous VERSION properties and refuses incompatible target layout versions.

## Dependencies and Integration Points
The class uses `StorageDirectory`, `Storage`, `StorageInfo`, `NNStorage.rename/deleteDir`, `Preconditions`, and Java NIO file walking/link creation. It is called by `FSImage` upgrade, rollback, and finalize code, and its behavior must stay compatible with journal managers that implement similar stages.

## Risks and Edge Cases
- Hard-link creation in `doPreUpgrade` requires filesystem support and same-volume semantics; failures abort the upgrade.
- Preconditions intentionally fail if temp directories already exist, forcing restart/recovery rather than guessing.
- `canRollBack` returns false for dirs without `previous` after reading current properties, but throws for present `previous` with incompatible layout.
- Rollback deletes the current state after moving it aside; operator confirmation happens in higher-level `NameNode.doRollback`.

## Test Signals
Upgrade and rollback behavior is exercised indirectly by `TestStartup`, `TestSecondaryNameNodeUpgrade`, rolling-upgrade tests, and rollback/recovery tests under the NameNode test package. Focused validation should cover interrupted pre-upgrade temp directories, hard-link failures, and layout-version mismatch errors.
