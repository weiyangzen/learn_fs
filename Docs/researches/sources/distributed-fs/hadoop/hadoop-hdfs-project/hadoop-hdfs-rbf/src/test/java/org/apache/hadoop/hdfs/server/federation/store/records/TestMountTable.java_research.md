# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestMountTable.java

Purpose: `TestMountTable` validates the `MountTable` record model used by RBF to map a source path to one or more remote namespace destinations, plus routing order, readonly state, fault-tolerance state, quotas, dates, validation, and serialization.

Important fields and APIs: the fixture uses source `/test`, two destinations (`ns0 -> /path1`, `ns1 -> /path/path2`), linked-map destination ordering, explicit created/modified dates, `DestinationOrder` values, and a `RouterQuotaUsage` object with namespace and storage-space counts/quotas. It checks `MountTable.newInstance()` overloads, `getDestinations()`, `getDefaultLocation()`, `setReadOnly()`, `setFaultTolerant()`, `setDestOrder()`, `setQuota()`, and `StateStoreSerializer`.

Control flow and state behavior: `testGetterSetter()` validates default fields, default quota reset values from `HdfsConstants.QUOTA_RESET`, default `DestinationOrder.HASH`, and explicit dates. `testSerialization()` repeats serialization checks for `RANDOM`, `HASH`, and `LOCAL` orders while preserving readonly and quota state. `testReadOnly()`, `testFaultTolerant()`, `testOrder()`, and `testQuota()` isolate each feature flag or field group.

Validation behavior: `testValidation()` asserts invalid source paths without a leading slash, destination paths without a leading slash, and empty destination namespace IDs throw exceptions containing the specific `MountTable` validation messages. A valid destination map then creates a non-null record.

Dependencies and integration points: the test integrates `RemoteLocation`, `DestinationOrder`, `RouterQuotaUsage`, `HdfsConstants`, `GenericTestUtils`, and the state-store serializer. It gives store-level tests a record contract for comparing mount-table destinations and replacement behavior.

Risks and test signals: ordered `RemoteLocation` comparison relies on linked insertion order in the fixture. The equality check in `testFaultTolerant()` signals that fault-tolerant state participates in record equality. The validation checks make source and destination path normalization strict rather than forgiving.
