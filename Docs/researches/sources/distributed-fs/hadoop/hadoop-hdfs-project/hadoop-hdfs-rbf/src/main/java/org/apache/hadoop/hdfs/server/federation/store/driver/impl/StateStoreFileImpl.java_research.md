# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/driver/impl/StateStoreFileImpl.java

Purpose: Concrete local-disk implementation of the file-based state store driver. It maps `StateStoreFileBaseImpl` path primitives to `java.io.File` operations and UTF-8 buffered streams.

Important APIs/types/functions: configuration key `dfs.federation.router.store.driver.file.directory`; overrides `exists`, `mkdir`, `rename`, `remove`, `getRootDir`, `getConcurrentFilesAccessNumThreads`, `getReader`, `getWriter`, `getChildren`, and `close`.

Control flow: `getRootDir` lazily reads the configured directory, otherwise creates a temporary directory under `java.io.tmpdir` and logs a warning. Reads and writes open `FileInputStream`/`FileOutputStream` wrapped in UTF-8 readers/writers. Directory listing returns child file names for the base class to deserialize or clean.

State/persistence behavior: records persist as files under the configured or fallback local directory. `Files.move` from Hadoop's shaded Guava is used for commit rename, `File.delete` removes records, and `close` marks the driver uninitialized after shutting down base resources.

Dependencies/integration: local backend for tests and simple deployments; integrates with `RBFConfigKeys.FEDERATION_STORE_FILE_ASYNC_THREADS` for optional parallel access and the base serializer for payload format.

Risks: fallback to a temporary directory can make state ephemeral if the required path is not configured; local file rename semantics vary across filesystems; `File.delete` failure is silent except through the base class return path; null reader/writer after open failure causes base operations to fail later.

Test signals: local driver tests should configure an explicit directory, verify temp-directory fallback only when intended, exercise rename overwrite behavior, UTF-8 serialization, child listing, close/reinitialize, and async thread configuration.
