# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/StateStoreRecordOperations.java

## Purpose
`StateStoreRecordOperations` defines the CRUD contract that every state-store driver must expose for `BaseRecord` types.

## Important APIs, Types, And Functions
The interface declares `get`, single-query `get`, `getMultiple`, `put`, `putAll`, `remove(record)`, `removeMultiple`, `removeAll`, query-based `remove`, and multi-query `remove`. Methods are annotated with Hadoop retry semantics: reads are `@Idempotent`, writes/removes are `@AtMostOnce`.

## Control Flow
Implementations fetch records by class, optionally filter by `Query`, create/update records with conflict flags, and remove records by object, class, or query.

## State, Persistence, And Dependencies
The interface has no state. Persistent behavior is defined by concrete drivers. It depends on `BaseRecord`, `Query`, `QueryResult`, and `StateStoreOperationResult`.

## Integration Points
`StateStoreDriver` implements this interface. Record stores use it to persist memberships, mount tables, router state, and disabled nameservices.

## Risks
Default implementations in `StateStoreBaseImpl` require `get` to return fresh record instances. Backend-specific filtering and atomicity vary by driver. `allowUpdate` and `errorIfExists` semantics must be implemented consistently.

## Test Signals
Driver compliance tests should cover all CRUD methods, query filtering, duplicate single-query detection, conflict flags, bulk partial failures, retry annotations, and freshness of returned records.
