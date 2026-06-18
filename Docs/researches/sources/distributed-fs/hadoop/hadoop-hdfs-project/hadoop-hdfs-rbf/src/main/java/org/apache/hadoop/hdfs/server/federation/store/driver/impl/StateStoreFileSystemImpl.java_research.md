# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreFileSystemImpl.java

Purpose: Hadoop `FileSystem` implementation of the file-based state store, typically backed by HDFS through `dfs.federation.router.store.driver.fs.path`.

Important APIs/types/functions: overrides the same path and stream primitives as `StateStoreFileImpl`; uses `FileSystem.exists`, `mkdirs`, `FileUtil.rename(..., Options.Rename.OVERWRITE)`, `delete`, `open`, `create`, and `listStatus`.

Control flow: `getRootDir` parses the configured URI, obtains the matching Hadoop `FileSystem`, and returns null on invalid configuration so base initialization fails. Reads/writes use `FSDataInputStream` and `FSDataOutputStream`. Children are listed from the working path and converted to simple names.

State/persistence behavior: persists each state-store record as UTF-8 serialized content in the configured filesystem namespace. Commits overwrite the final path via filesystem rename; `remove` deletes recursively; `close` closes both base resources and the `FileSystem` handle.

Dependencies/integration: integrates Router federation with any Hadoop `FileSystem` implementation, with async thread count controlled by `RBFConfigKeys.FEDERATION_STORE_FS_ASYNC_THREADS`.

Risks: invalid or missing URI makes the driver unavailable; HDFS/file-system rename guarantees and overwrite behavior are backend-dependent; `getChildren` constructs `new Path(workPath, pathName)` even when `pathName` is already full, so tests should guard path resolution; recursive delete can remove unexpected descendants.

Test signals: integration tests need a MiniDFSCluster or mock filesystem to verify URI initialization, directory creation, overwrite rename, list/read/write semantics, close behavior, and failure metrics when the filesystem is unavailable.
