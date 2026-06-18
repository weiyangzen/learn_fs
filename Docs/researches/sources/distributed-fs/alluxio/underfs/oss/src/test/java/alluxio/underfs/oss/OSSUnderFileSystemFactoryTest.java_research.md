# sources/distributed-fs/alluxio/underfs/oss/src/test/java/alluxio/underfs/oss/OSSUnderFileSystemFactoryTest.java

## Purpose
This is a factory registration smoke test for Aliyun OSS.

## Important APIs, Types, And Functions
The `factory` test calls `UnderFileSystemFactoryRegistry.find("oss://test-bucket/path", Configuration.global())` and asserts that a factory is present.

## Control Flow
The registry scans available UFS factory providers and should select the OSS factory for the `oss://` scheme.

## State And Persistence
No external state is used.

## Dependencies And Integration Points
It checks module service registration rather than OSS client behavior.

## Risks
It does not validate `create`, credentials, STS mode, or negative scheme matching.

## Test Signals
Passing confirms that the OSS module is discoverable by Alluxio when present on the classpath.
