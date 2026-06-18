# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractPathHandle.java

## Purpose
`TestRawlocalContractPathHandle` runs durable path-handle contract tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractPathHandleTest`, has a default constructor, and creates `RawlocalFSContract`.

## Control Flow
Inherited tests obtain path handles, mutate or rename files as required by the abstract suite, and check reference/content constraints.

## State And Persistence
No subclass state. Raw local files are created and mutated by inherited tests.

## Dependencies And Integration Points
It exercises path-handle support advertised by the rawlocal contract.

## Risks
Path-handle durability depends on file identity semantics of the host filesystem.

## Test Signals
Signals are path handles resolving correctly or rejecting changed content according to contract flags.
