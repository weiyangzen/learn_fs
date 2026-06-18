# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/fs/contract/router/RouterHDFSContract.java

`RouterHDFSContract` adapts Hadoop's generic `HDFSContract` to a Router-Based Federation mini cluster. It supplies the `FileSystem` under test for the many `AbstractContract*Test` subclasses in this package.

Important APIs are the static lifecycle methods `createCluster()`, `createCluster(boolean security)`, `createCluster(boolean ha, int numNameServices, boolean security)`, `destroyCluster()`, `getCluster()`, `getRouterCluster()`, and `getFileSystem()`, plus the override `getTestFileSystem()`. `BLOCK_SIZE` is tied to `AbstractFSContractTestBase.TEST_FILE_LEN`.

Control flow creates optional secure configuration through `SecurityConfUtil`, builds a `MiniRouterDFSCluster`, starts namenodes/datanodes, starts routers, registers namenodes with all routers, installs mock mount locations, transitions one namenode per nameservice active in HA mode, and waits for active namespace discovery. Teardown shuts the cluster down and destroys the security context.

State is a static `MiniRouterDFSCluster`, so tests rely on class-level setup/teardown isolation. Dependencies include `MiniDFSCluster`, `MiniRouterDFSCluster`, `SecurityConfUtil`, JUnit assertions, and federation test constants. Integration points are Router RPC clients and mock mount-table resolution. Risks are static-state leakage between contract suites, partial startup cleanup, random router selection hiding per-router issues, and security context cleanup failures. Test signals are all RPC contract subclasses that instantiate this contract in secure and non-secure modes.
