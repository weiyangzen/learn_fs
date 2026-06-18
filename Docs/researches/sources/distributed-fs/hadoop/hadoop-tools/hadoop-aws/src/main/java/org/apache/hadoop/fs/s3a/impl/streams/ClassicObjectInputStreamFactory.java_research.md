# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/ClassicObjectInputStreamFactory.java

## Purpose
`ClassicObjectInputStreamFactory` creates the traditional `S3AInputStream` implementation and declares its stream capabilities.

## Important APIs and Types
`readObject(ObjectReadParameters)` returns a new `S3AInputStream`. `hasCapability()` adds IO statistics context, readahead, unbuffer, and vectored IO capabilities before delegating to base capability checks. `streamType()` returns `Classic`. `factoryRequirements()` returns vectored IO context from configuration and no extra threads.

## Control Flow
S3A store delegates stream creation here when configured for classic streams. Capability queries are normalized and matched against known stream capability constants.

## State and Persistence
The factory has service lifecycle state inherited from `AbstractService` but no custom mutable state. It creates read streams only.

## Dependencies and Integration Points
It depends on `S3AInputStream`, `ObjectReadParameters`, stream capability constants, and `StreamIntegration.populateVectoredIOContext`.

## Risks and Edge Cases
Capability declarations must match actual `S3AInputStream` behavior. Changes to classic stream features require updating this factory.

## Test Signals
Tests should verify stream type, created class, capability responses, and vectored IO configuration propagation.
