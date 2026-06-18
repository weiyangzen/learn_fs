# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/RollingUpgradeInfo.java

## Purpose
`RollingUpgradeInfo` extends `RollingUpgradeStatus` with rolling-upgrade timing and rollback-image state.

## APIs and Behavior
The constructor sets block pool ID, rollback image flag, start time, and finalize time, passing finalized status to the superclass based on nonzero finalize time. It exposes `createdRollbackImages`, setter for that flag, `isStarted`, `getStartTime`, `isFinalized`, `finalize(finalizeTime)`, and `getFinalizeTime`. Equality and hash include superclass identity plus times. `toString()` renders start/finalize times with readable date and raw timestamp. Nested `Bean` exposes JMX-style fields.

## State, Dependencies, and Integration
The class is mutable for finalize time and rollback image flag. It integrates with `ClientProtocol.rollingUpgrade`, admin CLI/JMX, and NameNode upgrade state persisted elsewhere.

## Risks and Test Signals
Calling `finalize(0)` is ignored; finalizing with nonzero time clears rollback image state. Tests should cover not-started/not-finalized rendering, equality before/after finalize, Bean values, rollback image flag changes, and RPC behavior for query/prepare/finalize actions.
