# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractSeek.java

## Purpose
`TestRawlocalContractSeek` runs common seek tests against raw local FS.

## Important APIs, Types, And Functions
It extends `AbstractContractSeekTest` and creates `RawlocalFSContract`.

## Control Flow
Inherited tests create datasets, perform seek/read/positioned-read operations, and check EOF/negative/closed-stream behavior.

## State And Persistence
No subclass state. Raw local files are temporary.

## Dependencies And Integration Points
It exercises raw local input stream seeking.

## Risks
Platform stream behavior after close or EOF can differ from remote filesystems but should match rawlocal contract flags.

## Test Signals
Signals are exact byte comparisons after seeks and expected exceptions.
