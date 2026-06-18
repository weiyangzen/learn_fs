# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractRename.java

## Purpose
`TestLocalFSContractRename` runs generic rename contract tests against local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractRenameTest` and creates `LocalFSContract`.

## Control Flow
Inherited tests validate file and directory rename behavior, destination handling, missing source behavior, and overwrite semantics according to local contract flags.

## State And Persistence
The subclass stores no state. Test paths are local files/directories created and renamed under the test root.

## Dependencies And Integration Points
It exercises `LocalFileSystem.rename()` through contract expectations.

## Risks
Windows rename behavior differs for open files and destination directories; contract flags and local raw fallback behavior must account for this.

## Test Signals
Signals are returned boolean values, source absence, destination presence, and preserved file contents after rename.
