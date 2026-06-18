# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractOpen.java

## Purpose
`TestRawlocalContractOpen` runs generic open/read tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractOpenTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create files, open streams, read and compare contents, and validate invalid open behavior.

## State And Persistence
No subclass fields. Raw local files are temporary.

## Dependencies And Integration Points
It exercises raw local input stream behavior without checksum validation.

## Risks
Direct OS reads may behave differently around locked or deleted files on Windows.

## Test Signals
Signals are byte equality and expected missing-path/directory-open failures.
