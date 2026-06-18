# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/lib/service/hadoop/TestFileSystemAccessService.java

Purpose: Integration tests for `FileSystemAccessService`, including security mode validation, Hadoop config loading, namenode whitelisting, filesystem creation/execution, exception handling, and cache eviction.

Important APIs/types/functions: `createHadoopConf`, `simpleSecurity`, Kerberos misconfiguration tests, `serviceHadoopConf`, `serviceHadoopConfCustomDir`, `inWhitelists`, `NameNodeNotinWhitelists`, `createFileSystem`, `fileSystemExecutor`, `fileSystemExecutorNoNameNode`, `fileSystemExecutorException`, and `fileSystemCache`.

Control flow: most tests build a `Server` with `InstrumentationService`, `SchedulerService`, and `FileSystemAccessService`. Config tests write `hdfs-site.xml` in the server config dir or custom dir. Security tests assert expected `ServiceException` codes for missing Kerberos keytab/principal, failed Kerberos login, and unknown auth type. Filesystem tests point the service at `TestHdfsHelper`, create/release filesystems, run executor callbacks, verify released filesystems are closed, translate callback exceptions to `H03`, and test cache reuse/purge across sleeps.

State and persistence: writes Hadoop XML config under `@TestDir`, uses MiniDFS for HDFS-backed tests, and relies on server services plus scheduler-driven cache purging. Cache state is time-based and lease-count-based.

Dependencies/integration: HTTPFS server container, instrumentation and scheduler services, HDFS mini-cluster, Hadoop `FileSystem`, UGI/security configuration, and custom exception annotations.

Risks and test signals: strong signal for filesystem access lifecycle and cleanup. Timing in `fileSystemCache` can be flaky on slow machines, and Kerberos failure tests intentionally depend on invalid local paths/principals.
