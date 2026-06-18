## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/TestFsShellList.java

Purpose: tests `FsShell -ls` on local files, including checksum-enabled files, special character names on non-Windows platforms, quoted output mode, and security configuration validation.

Important APIs/types/functions: `FsShell.run`, `LocalFileSystem`, `FileSystem.getLocal`, `setVerifyChecksum`, `setWriteChecksum`, `getChecksumFile`, `CommonConfigurationKeysPublic.HADOOP_SECURITY_AUTHENTICATION`, and AssertJ/JUnit assertions.

Control flow: `@BeforeAll` creates a local shell and test root with checksum verification/writing enabled. `createFile` writes a local file and asserts its checksum sidecar exists. `testList` lists the root after creating normal files and, on non-Windows, names with backspace/tab/carriage-return characters; it also runs `-ls -q`. `testListWithUGI` sets an invalid authentication method and expects `IllegalArgumentException`.

State and persistence: creates local files under `test.build.data` and removes the root in `@AfterAll`. Static shell/local FS state persists across tests.

Dependencies/integration points: local filesystem listing, checksum sidecar behavior, special-character rendering, shell quote mode, and UGI/security config initialization.

Risks and test signals: platform-specific filename legality is handled by skipping special names on Windows. Failures point to list command formatting, security config validation, or local checksum setup.
