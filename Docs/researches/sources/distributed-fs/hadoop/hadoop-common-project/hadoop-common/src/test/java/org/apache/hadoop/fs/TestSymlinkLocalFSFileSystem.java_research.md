# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestSymlinkLocalFSFileSystem.java

Purpose: runs the local symlink suite through the `FileSystem` API and documents local/ChecksumFS deviations from the generic symlink contract.

Important APIs/types/functions: `FileSystem.getLocal`, `FileSystemTestWrapper`, inherited `TestSymlinkLocalFS`, `Options.Rename`, `FileAlreadyExistsException`, `FileNotFoundException`, and disabled inherited tests.

Control flow/state/persistence: `@BeforeAll` installs a FileSystem wrapper. Several inherited tests are disabled because raw local mkdir/create behavior and ChecksumFileSystem append support differ from generic expectations. The class overrides symlink-to-self rename to assert failure both without and with overwrite; overwrite currently accepts either already-exists or not-found due to a known HADOOP-9819 issue.

Dependencies/integration points: validates local symlink behavior through FileSystem and the checksum wrapper stack, not FileContext.

Risks/test signals: protects documented deviations and catches rename-to-self regressions. Disabled tests are risk markers where local FS does not meet generic contract assumptions.
