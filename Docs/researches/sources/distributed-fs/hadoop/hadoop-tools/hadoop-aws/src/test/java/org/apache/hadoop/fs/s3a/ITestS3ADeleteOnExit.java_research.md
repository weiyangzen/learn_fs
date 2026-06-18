# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3ADeleteOnExit.java

Purpose: Validates Hadoop `deleteOnExit()` behavior for S3A across nonexistent paths, existing files, paths registered before creation, and recursive directory cleanup.

Important APIs/types/functions: `FileSystem.deleteOnExit()`, `S3AFileSystem.initialize()`, `ContractTestUtils.createFile()`, `dataset()`, and inherited `assertPathExists()`/`assertPathDoesNotExist()`.

Control flow: creates a separate `S3AFileSystem` instance, builds test paths, registers missing and future paths with delete-on-exit, writes files and a subdirectory, closes the separate filesystem, then verifies all registered paths were removed through the base filesystem.

State and persistence: uses a distinct filesystem object with its own delete-on-exit set; remote S3 objects/directories are persisted until close triggers cleanup.

Dependencies and integration points: Hadoop `FileSystem` close lifecycle, S3A recursive delete, and delete-on-exit path set ordering.

Risks: delete-on-exit state is per-filesystem instance; object-store eventual/listing behavior can affect recursive directory verification; failure to close would leave test data.

Test signals: ensures registered cleanup executes on close even when paths were missing at registration time or are directories containing later-created files.
