# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/ha/StandbyState.java

## Purpose

`StandbyState.java` implements standby and observer HA states for the NameNode. The source was read as a complete 121-line file.

## Important APIs, Types, and Functions

The class extends `HAState`, stores `isObserver`, and implements `setState`, `enterState`, `prepareToExitState`, `exitState`, `checkOperation`, `shouldPopulateReplQueues`, and `toString`.

## Control Flow

Constructors choose `HAServiceState.STANDBY` or `OBSERVER`. Standby can transition to active or observer; observer can transition to standby. Entering starts standby services, preparing to exit asks the context to prepare stopping standby services, and exiting stops standby services. Operation checks allow unchecked operations and reads only when stale reads are allowed. Observer write attempts throw `ObserverRetryOnActiveException`; other disallowed operations throw `StandbyException`.

## State and Persistence Behavior

The class itself has only the observer flag and inherited transition time. Standby services include edit tailing and checkpointing that maintain local namespace state from persisted journals.

## Dependencies and Integration Points

It integrates with `HAContext`, `NameNode.ACTIVE_STATE`, `STANDBY_STATE`, `OBSERVER_STATE`, `OperationCategory`, `StandbyException`, and `ObserverRetryOnActiveException`.

## Risks and Edge Cases

Observer read behavior depends on `allowStaleReads`. Access-time updates can turn opens into writes, so observer write rejection intentionally directs clients to retry on active.

## Test Signals

Tests should cover standby and observer transition matrix, operation categories, stale read allowance, observer write retry exception type, replication queue non-population, and service lifecycle hook failures.
