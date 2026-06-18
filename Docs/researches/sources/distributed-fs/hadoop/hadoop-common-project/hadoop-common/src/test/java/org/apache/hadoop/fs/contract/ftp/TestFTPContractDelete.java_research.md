# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractDelete.java

## Purpose
`TestFTPContractDelete` runs the generic delete contract suite against FTP.

## Important APIs, Types, And Functions
The only local API is `createContract(Configuration)`, returning `FTPContract`. The inherited suite supplies delete tests for files, directories, missing paths, recursive flags, and root-safety behavior.

## Control Flow
Base setup creates an FTP-backed test directory. The inherited delete tests create filesystem entries, call `FileSystem.delete()`, and assert return values plus final path state.

## State And Persistence
The class has no fields. Persistent effects are FTP objects created and removed by inherited tests.

## Dependencies And Integration Points
It connects `AbstractContractDeleteTest` to `FTPContract` and the configured FTP server.

## Risks
FTP delete semantics and server permissions can vary; false failures may indicate wrong FTP user permissions rather than Hadoop API regressions.

## Test Signals
Passing tests show delete return values and namespace effects match the FTP contract resource.
