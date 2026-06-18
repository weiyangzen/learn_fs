# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/records/TestRouterState.java

Purpose: `TestRouterState` validates the `RouterState` record model, serializer round trips, and state-store cache resilience when driver refreshes fail. It bridges record-level serialization with an in-memory mock driver and `MembershipNamenodeResolver`.

Important fields and APIs: `generateRecord()` creates a `RouterState` with address, start time, `RouterServiceState.RUNNING`, version, compile info, created/modified dates, and nested `StateStoreVersion` containing a mount-table version. `validateRecord()` checks address, start time, status, compile info, version, and nested mount-table version. Serialization uses `StateStoreSerializer`.

Control flow and resilience behavior: `testGetterSetter()` and `testSerialization()` validate the record directly and after serializer round trip. `testStateStoreResilience()` creates a `StateStoreService` configured with `MockStateStoreDriver`, disables router metrics, inserts two `MembershipState` records for the same block pool with active and standby NameNodes, loads the driver, constructs a `MembershipNamenodeResolver`, refreshes caches, and verifies two NameNodes are resolved for the block pool. It then enables induced driver I/O errors, refreshes caches again, verifies the service cache update time did not advance, and confirms the resolver still returns the prior two cached NameNodes.

Dependencies and integration points: the file depends on RBF config keys, `StateStoreService`, `StateStoreDriver`, `MockStateStoreDriver`, `MembershipState`, `MembershipNamenodeResolver`, federation resolver context interfaces, and router/name-node service enums. It is the main local test proving cache refresh failure should preserve previously valid cache state.

Risks and test signals: the resilience test creates and stops a real `StateStoreService` manually and must clean up to avoid leaking state. It signals a key operational requirement: transient state-store read failures must not erase router resolver knowledge or advance cache timestamps as if refresh succeeded.
