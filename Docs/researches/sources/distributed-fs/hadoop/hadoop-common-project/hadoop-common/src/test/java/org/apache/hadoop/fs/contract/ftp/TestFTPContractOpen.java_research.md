# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractOpen.java

## Purpose
`TestFTPContractOpen` runs common open/read contract behavior against FTP.

## Important APIs, Types, And Functions
It extends `AbstractContractOpenTest` and returns `FTPContract`. The actual assertions are inherited.

## Control Flow
Inherited tests create files, open them through `FileSystem.open()`, read expected data, and test missing path or directory-open behavior as described by contract options.

## State And Persistence
Only inherited test files under the FTP test directory persist during a test.

## Dependencies And Integration Points
It connects FTP to the generic open suite and exercises the FTP input stream path in `FTPFileSystem`.

## Risks
Network transfer mode, server data connection policy, and user permissions can affect read behavior independently of Hadoop contract logic.

## Test Signals
Successful full-data reads and expected failures for invalid opens indicate FTP stream integration is working.
