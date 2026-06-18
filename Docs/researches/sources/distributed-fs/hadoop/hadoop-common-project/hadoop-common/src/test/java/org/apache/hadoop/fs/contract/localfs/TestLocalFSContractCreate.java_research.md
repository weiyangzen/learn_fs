# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractCreate.java

## Purpose
`TestLocalFSContractCreate` runs the generic create contract suite against local FS and adds a regression check for sync semantics when checksum writing is disabled.

## Important APIs, Types, And Functions
It extends `AbstractContractCreateTest`, returns `LocalFSContract`, and defines `testSyncablePassthroughIfChecksumDisabled()`. That test wraps the raw filesystem in a `LocalFileSystem`, calls `setWriteChecksum(false)`, and invokes inherited `validateSyncableSemantics()`.

## Control Flow
Generic create tests are inherited. The custom test obtains the current `LocalFileSystem`, constructs a new `LocalFileSystem` around its raw FS, disables checksum output, then verifies `Syncable` semantics and immediate metadata updates.

## State And Persistence
The test creates local files under the test root. The temporary `LocalFileSystem` wrapper is closed with try-with-resources.

## Dependencies And Integration Points
It depends on `LocalFileSystem`, raw local FS passthrough, and abstract create-suite sync validation.

## Risks
Checksum-disabled local FS must not accidentally keep the same delayed/checksum behavior. On unsupported platforms, raw local metadata timing can vary.

## Test Signals
The custom signal is successful sync/hsync/hflush-style validation with immediate file status visibility after checksumming is disabled.
