# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/sftp/TestSFTPContractSeek.java

## Purpose
`TestSFTPContractSeek` runs common seek tests against the embedded SFTP contract.

## Important APIs, Types, And Functions
It extends `AbstractContractSeekTest` and creates `SFTPContract`.

## Control Flow
Inherited tests run after `SFTPContract` starts an embedded server. They create test files over SFTP, seek/read ranges, and verify contract-defined EOF and invalid-position behavior.

## State And Persistence
No subclass fields. Remote-visible files are backed by the embedded server and cleaned after tests.

## Dependencies And Integration Points
It exercises `SFTPFileSystem` seek support through Apache SSHD.

## Risks
Network-style streams may not support all seek behavior efficiently; server startup/caching misconfiguration can make failures look like seek issues.

## Test Signals
Signals are exact data after seeks and clean embedded server lifecycle.
