# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/rbfbalance/TestMountTableProcedure.java

This class tests `MountTableProcedure`, the RBF balance procedure that rewrites a mount-table entry and toggles mount-point writability during migration.

Global setup starts a `StateStoreDFSCluster` with a Router configured for state store, admin, and RPC. It registers active namenode reports for `ns0` and `ns1`, refreshes caches, and builds `routerConf` pointing at the Router admin address. Each test synchronizes a mock mount table into the state store and resets the Router admin client.

`testUpdateMountpoint()` adds `/test-path`, disables writes, executes a `MountTableProcedure` to move the destination to `ns1:/test-dst`, reloads state-store cache, verifies destination update, reenables writes, and confirms the path now fails with no available namenode rather than read-only. `testDisableAndEnableWrite()` directly verifies read-only enforcement and reenablement. `testSeDeserialize()` writes and reads the procedure through Hadoop `Writable` APIs and checks persisted fields.

State and persistence are the Router state store, mount table records, state-store cache, and procedure serialization bytes. Dependencies include `MountTableManager`, `MountTableStoreImpl`, `DFSClient`, HA state reports, and `LambdaTestUtils.intercept`. Risks include dependence on error-message text and only one Router context. Test signal covers admin RPC integration, cache reload, read-only enforcement, destination mutation, and serialization.
