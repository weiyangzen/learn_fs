# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/localfs/TestLocalFSContractGetEnclosingRoot.java

## Purpose
`TestLocalFSContractGetEnclosingRoot` verifies local filesystem behavior for resolving the enclosing filesystem root of paths.

## Important APIs, Types, And Functions
It extends `AbstractContractGetEnclosingRoot` and returns `LocalFSContract`.

## Control Flow
The inherited suite creates or resolves local paths and checks that the filesystem reports the expected enclosing root for qualified and relative paths.

## State And Persistence
No subclass state is kept; any path creation is inherited and under the test directory.

## Dependencies And Integration Points
The class connects local FS to root-resolution contract behavior.

## Risks
Windows drive roots, URI qualification, and path normalization can change expected roots.

## Test Signals
Expected root `Path` values for local paths should match platform semantics.
