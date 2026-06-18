# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/ftp/TestFTPContractCreate.java

## Purpose
`TestFTPContractCreate` runs the generic create-file contract suite against `FTPContract`.

## Important APIs, Types, And Functions
It extends `AbstractContractCreateTest` and overrides `createContract(Configuration)` to return `new FTPContract(conf)`.

## Control Flow
All test flow is inherited: the abstract suite creates files, tests overwrite behavior, parent-directory expectations, stream semantics, and error handling according to FTP contract options.

## State And Persistence
State is inherited from the base class and consists of files created under the FTP test directory. There is no local state in this subclass.

## Dependencies And Integration Points
The class integrates FTP configuration/resource loading with `AbstractContractCreateTest`.

## Risks
FTP servers may expose different overwrite or parent creation behavior than POSIX filesystems; contract XML must describe those differences accurately.

## Test Signals
Signals are inherited create-contract assertions passing or skipping based on FTP feature flags, with cleanup removing created remote files.
