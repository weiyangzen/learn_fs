# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractAppend.java

## Purpose
`TestLocalFSContractAppend` runs the generic append contract suite against the checksummed local filesystem.

## Important APIs, Types, And Functions
It extends `AbstractContractAppendTest` and returns `LocalFSContract` from `createContract()`.

## Control Flow
Inherited tests create files, append data through `FSDataOutputStream`, verify final contents, and exercise edge cases such as appending to missing paths or open-file rename behavior as supported.

## State And Persistence
No local fields are stored. Files and local checksum side files may be created under the test root.

## Dependencies And Integration Points
The class connects `AbstractContractAppendTest` to `LocalFileSystem`.

## Risks
Checksum side files can affect raw file observations and cleanup. Platform filesystem semantics can alter append and rename behavior.

## Test Signals
Final file contents, lengths, and expected append failures are the main signals.
