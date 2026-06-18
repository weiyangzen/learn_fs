# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/test/java/org/apache/hadoop/fs/contract/rawlocal/TestRawlocalContractGetEnclosingRoot.java

## Purpose
`TestRawlocalContractGetEnclosingRoot` verifies root resolution for raw local paths.

## Important APIs, Types, And Functions
It extends `AbstractContractGetEnclosingRoot` and creates `RawlocalFSContract`.

## Control Flow
Inherited root-resolution cases run against raw local FS.

## State And Persistence
The subclass stores no state. Any test paths are temporary local paths.

## Dependencies And Integration Points
It connects raw local filesystem to generic root-resolution contract behavior.

## Risks
Windows drive letters and URI/path qualification can produce platform-specific root values.

## Test Signals
Signals are expected enclosing root paths for qualified raw local paths.
