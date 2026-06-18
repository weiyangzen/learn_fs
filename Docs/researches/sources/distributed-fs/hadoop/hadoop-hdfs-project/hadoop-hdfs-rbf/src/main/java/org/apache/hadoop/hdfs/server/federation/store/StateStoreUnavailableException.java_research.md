# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/StateStoreUnavailableException.java

## Purpose
`StateStoreUnavailableException` signals that the state-store backend or cache is not ready for an operation.

## Important APIs, Types, And Functions
It extends `IOException`, defines `serialVersionUID`, and has a message constructor.

## Control Flow
There is no internal control flow beyond exception construction.

## State, Persistence, And Dependencies
No state beyond the exception message exists. There is no persistence.

## Integration Points
`StateStoreDriver.verifyDriverReady` and `CachedRecordStore.checkCacheAvailable` throw this exception. Router callers can treat it as retryable state-store unavailability.

## Risks
Because it is an `IOException`, generic IO handling may hide the specific retry signal unless callers check the type.

## Test Signals
Tests should verify specific exception propagation from unavailable driver/cache paths and client retry behavior.
