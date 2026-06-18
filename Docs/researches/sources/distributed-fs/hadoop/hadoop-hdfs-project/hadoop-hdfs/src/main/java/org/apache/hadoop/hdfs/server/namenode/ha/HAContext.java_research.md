# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/HAContext.java

## Purpose

`HAContext.java` defines the context operations that HA state objects use to manipulate a NameNode. The source was read as a complete 86-line file.

## Important APIs, Types, and Functions

The interface declares state accessors, active and standby service start/stop methods, standby prepare-to-stop hook, namesystem write lock/unlock, `checkOperation`, and `allowStaleReads`.

## Control Flow

There is no implementation flow. `HAState` calls these methods during transitions and operation checks. Implementations provide the actual NameNode service lifecycle behavior.

## State and Persistence Behavior

The interface owns no state. Implementations control persistent side effects indirectly by starting edit-log writers, tailers, checkpointing, block managers, and RPC services appropriate to active or standby state.

## Dependencies and Integration Points

It integrates with `HAState`, `ServiceFailedException`, `NameNode.OperationCategory`, and `StandbyException`.

## Risks and Edge Cases

The comments call out a race where clients can block behind a standby holding the namesystem lock; operation checks should happen both before and after lock acquisition in relevant callers. Incorrect implementation can allow writes in standby or fail to stop checkpointing before activation.

## Test Signals

Tests should verify state classes call context methods in the expected order, operation checks are enforced around locks, stale-read configuration is honored, and service lifecycle failures propagate as transition failures.
