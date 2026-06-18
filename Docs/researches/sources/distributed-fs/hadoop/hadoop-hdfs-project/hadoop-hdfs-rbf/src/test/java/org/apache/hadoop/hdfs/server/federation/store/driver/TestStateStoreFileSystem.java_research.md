# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/store/driver/TestStateStoreFileSystem.java

Purpose: `TestStateStoreFileSystem` applies the shared driver conformance suite to `StateStoreFileSystemImpl`, the FileSystem-backed state-store implementation, using a real `MiniDFSCluster` as the backing filesystem.

Important APIs and helpers: `setupCluster()` builds a `Configuration` for `StateStoreFileSystemImpl`, sets `StateStoreFileSystemImpl.FEDERATION_STORE_FS_PATH` to `/hdfs-federation/`, sets `FEDERATION_STORE_FS_ASYNC_THREADS` to the parameter value, starts a one-datanode `MiniDFSCluster`, waits for it to become available, and initializes the base state store. Tests are parameterized over async-thread values `20` and `0`.

Control flow and persistence behavior: the normal insert, update, delete, fetch-error, and metrics tests delegate to `TestStateStoreDriverBase` after removing all existing records. `testInsertWithErrorDuringWrite()` wraps the driver with a Mockito spy, intercepts `getWriter()`, returns a spy `BufferedWriter`, forces `write(String)` to throw `IOException`, and then verifies through the base helper that no `MembershipState` record was inserted after the failed write. `testCacheLoadMetrics()` expects two refreshes to add two cache-load samples.

Dependencies and integration points: this test integrates HDFS `MiniDFSCluster`, `StateStoreFileBaseImpl`, `StateStoreFileSystemImpl`, Mockito stubbing, and the shared RBF driver base. It exercises real filesystem semantics such as directory creation, writer failure, and cleanup through the state-store driver abstraction.

Risks and test signals: the MiniDFSCluster dependency makes the test heavier than the local file test. It strongly signals atomicity expectations for file-backed writes: if serialization or write fails, no partial logical record should be visible. The parameterization requires synchronous and asynchronous filesystem modes to behave identically from the driver API perspective.
