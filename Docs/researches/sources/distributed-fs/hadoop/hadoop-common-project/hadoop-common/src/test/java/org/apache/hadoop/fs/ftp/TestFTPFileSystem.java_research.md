# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/ftp/TestFTPFileSystem.java

## Purpose
`TestFTPFileSystem` directly tests core `FTPFileSystem` behavior outside the generic contract suites.

## Important APIs, Types, And Functions
Lifecycle methods `setUp()` and `tearDown()` create and remove a temp FTP root and embedded `FtpTestServer`. Tests cover create with and without write permissions, default port, transfer mode parsing, data connection mode parsing, permission-to-`FsAction` conversion, timeout configuration, and fully qualified path rename. Helpers include `getFTPFileOf()`, `enhancedAssertEquals()`, and `touch()`.

## Control Flow
Each test starts a fresh FTP server. Permission tests create users with or without `WritePermission`, configure `fs.defaultFS`, host, port, credentials, and disabled cache, then attempt writes/reads or expect an `IOException`. Mode tests configure strings and inspect `FTPClient` constants. The rename test creates qualified root-relative paths and verifies `fs.rename()` succeeds.

## State And Persistence
State is `server` and `testDir` per test. Temporary FTP home directories and files are recursively deleted in teardown.

## Dependencies And Integration Points
It depends on Commons Net FTP constants/client, Apache FTPServer users/permissions, Hadoop `FTPFileSystem`, `FileSystem`, `Path`, `FsAction`, and `LambdaTestUtils`.

## Risks
Tests are sensitive to FTP server permission semantics and cache disabling. String-based transfer/data-mode parsing defaults invalid values silently, so regressions could be missed if invalid inputs still map to defaults.

## Test Signals
Signals include round-trip written bytes, expected write-denied error text, default port equal to Commons Net FTP default, parsed mode constants, exact permission mapping, configured keepalive timeout, and successful qualified-path rename.
