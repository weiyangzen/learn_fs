# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractDelete.java

## Purpose
`TestLocalFSContractDelete` runs generic delete contract tests against checksummed local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractDeleteTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests create files and directories, delete them with recursive and non-recursive flags, and assert return values and final statuses.

## State And Persistence
The class has no fields. Local files and checksum side files are created transiently.

## Dependencies And Integration Points
It exercises `LocalFileSystem.delete()` through contract expectations.

## Risks
Deleting user data must also handle checksum side files; leftover checksum artifacts can pollute later tests.

## Test Signals
Correct delete return values and `FileNotFoundException`/absence checks after deletion are the main signals.
