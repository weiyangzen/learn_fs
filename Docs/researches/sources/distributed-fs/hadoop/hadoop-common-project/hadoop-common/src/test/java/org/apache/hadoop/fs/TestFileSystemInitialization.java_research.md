## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFileSystemInitialization.java

Purpose: tests filesystem creation edge cases: URL stream handler registration, missing optional filesystem libraries, and cleanup when `FileSystem.newInstance` initialization fails.

Important APIs/types/functions: `URL.setURLStreamHandlerFactory`, `FsUrlStreamHandlerFactory`, `FileSystem.getFileSystemClass`, `FileSystem.newInstance`, `LambdaTestUtils.intercept`, and inner `FailingFileSystem`.

Control flow: `testInitializationWithRegisteredStreamFactory` registers a Hadoop URL handler factory and then resolves the `file` filesystem class, allowing unrelated `IOException` but guarding against infinite recursion. `testMissingLibraries` expects failure for `s3a` when libraries are absent. `testNewInstanceFailure` registers `FailingFileSystem`, expects initialize failure, and verifies both initialize and close counters are incremented once.

State and persistence: registering a URL stream handler factory is JVM-global and can only be done once. `FailingFileSystem` uses static counters. No files are persisted.

Dependencies/integration points: integration with Java URL handling, service/provider discovery, optional S3A classpath behavior, and FileSystem lifecycle cleanup.

Risks and test signals: JVM-global URL factory registration can conflict with other tests. The cleanup assertion is important: a filesystem that fails during `initialize` must still be closed to avoid leaks, and close failures must not hide the original initialize error.
