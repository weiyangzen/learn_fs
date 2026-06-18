# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractOpen.java

## Purpose
`TestLocalFSContractOpen` runs common open/read contract tests against checksummed local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractOpenTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create local files, open them, read data, and validate errors for missing files or invalid open targets.

## State And Persistence
No subclass state. Local data and checksum files are created under the test root.

## Dependencies And Integration Points
It exercises `LocalFileSystem.open()` and checksum validation through the contract layer.

## Risks
Corrupt checksum side files can turn ordinary open/read tests into checksum failures.

## Test Signals
Read byte equality and expected failure types for invalid opens are the main signals.
