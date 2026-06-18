# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/FederationTestUtils.java

`FederationTestUtils` is a static utility collection for RBF tests. It creates synthetic federation records, waits for Router/namenode state-store visibility, performs common filesystem operations, mutates test clusters, and injects failures with Mockito/Whitebox.

Important APIs include `verifyException`, `createNamenodeReport`, overloaded `waitNamenodeRegistered`, `waitRouterRegistered`, file helpers (`addDirectory`, `createFile`, `readFile`, `deleteFile`, `countContents`, `checkForFileInDirectory`), JMX helper `getBean`, cluster transition helpers (`transitionClusterNSToStandby`, `transitionClusterNSToActive`), Router/FS client factories (`getFileSystem`, `getAdminClient`), `createMountTableEntry`, `refreshRoutersCaches`, `simulateSlowNamenode`, and `simulateThrowExceptionRouterRpcServer`.

Control flow is mostly synchronous helper logic. Wait methods poll with `GenericTestUtils.waitFor`; mount-table creation uses `RouterClient` admin APIs, writes `MountTable` records, refreshes Router caches, then reads entries back. Failure simulation wraps HA contexts or connection managers with spies and replaces private state via Whitebox.

State and persistence touched by this utility include HDFS files, mount-table state-store records, Router and membership caches, JMX MBeans, and mocked internal fields. Dependencies span HDFS, Router admin/state-store APIs, JMX, Mockito, and Hadoop test utilities.

Risks include reflection/Whitebox fragility, exact state polling timeouts, equality checks such as `getNamenodeId() == nnId || equals(nnId)` relying on a null-safe short-circuit, and broad helper scope making tests tightly coupled to internals. Test signal is indirect but extensive: many Router federation tests use these helpers for cluster setup, mount entries, failover state, and fault injection.
