# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractCreate.java

## Purpose
`TestRawlocalContractCreate` runs generic create contract tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractCreateTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create files, validate overwrite and parent behavior, and check stream semantics without checksum wrapping.

## State And Persistence
No subclass state. Raw OS files are created under the test root.

## Dependencies And Integration Points
It exercises `RawLocalFileSystem.create()` through the contract framework.

## Risks
Raw local create behavior varies with OS permissions and path normalization.

## Test Signals
Signals are successful data writes, expected overwrite outcomes, and correct file lengths.
