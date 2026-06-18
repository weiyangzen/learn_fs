# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/TestStateStoreDisabledNameservice.java

Purpose: verifies persistence and retrieval of disabled nameservice records in the state store.

Important APIs/types/functions: extends `TestStateStoreBase`; uses `DisabledNameservice`, `DisabledNameserviceStore`, `FederationStateStoreTestUtils.clearRecords`, `Set`, and JUnit assertions. `setup()` clears existing `DisabledNameservice` records before each test.

Control flow: `testDisableNameservice()` gets the disabled-nameservice store from the shared state store, creates disabled records for nameservices, inserts them through the store, retrieves the disabled set, and checks expected nameservice IDs and count. It validates both write and read paths for this record type.

State and persistence behavior: records are stored in the file-backed state-store driver supplied by `TestStateStoreBase`; setup clears only the relevant record type to isolate runs. Integration points include the state-store service, typed record store, and disabled nameservice record serialization. Risks include stale records if cleanup fails and set-order assumptions if future assertions become order-sensitive. Test signals are successful insertions and exact retrieved disabled nameservice set contents.
