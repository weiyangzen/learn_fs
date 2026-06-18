# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/RecordStore.java

## Purpose
`RecordStore` is the base abstraction for typed state-store API wrappers over a `StateStoreDriver`.

## Important APIs, Types, And Functions
It stores a record class and driver, exposes `getRecordClass` and `getDriver`, and provides static reflective factory `newInstance(Class<T>, StateStoreDriver)`.

## Control Flow
Subclasses call the protected constructor. `newInstance` looks for a public constructor taking `StateStoreDriver`, invokes it, logs errors, and returns null on failure.

## State, Persistence, And Dependencies
The class stores only the record type and driver reference. Persistence is handled by the driver and concrete stores.

## Integration Points
`StateStoreService.addRecordStore` uses `newInstance` to create `MembershipStoreImpl`, `MountTableStoreImpl`, `RouterStoreImpl`, and `DisabledNameserviceStoreImpl`.

## Risks
Factory failure returns null, and callers must avoid dereferencing without checks. Implementations need the expected constructor signature. Reflection errors are logged but not distinguished.

## Test Signals
Tests should cover factory success, missing constructor failure, driver/reference retention, and `StateStoreService` handling of factory failures.
