# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractMkdir.java

## Purpose
`TestFTPContractMkdir` binds the generic directory-creation contract tests to FTP.

## Important APIs, Types, And Functions
It extends `AbstractContractMkdirTest` and returns `FTPContract` from `createContract()`.

## Control Flow
Inherited tests create directories, repeated directories, nested parents, and file/directory conflict cases, with expectations controlled by FTP contract options.

## State And Persistence
No subclass state is stored. FTP directories are created under the configured test root and cleaned by the base class.

## Dependencies And Integration Points
It integrates FTP contract XML with the common mkdir suite.

## Risks
FTP servers can normalize paths or deny directory creation based on user home/root restrictions, so test setup must match the configured test directory.

## Test Signals
Signals are `mkdirs()` outcomes and subsequent `FileStatus` checks matching the contract.
