# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSUnderFileSystemFactory.java

## Purpose
This factory registers Aliyun OSS support with Alluxio's UFS factory mechanism.

## Important APIs, Types, And Functions
It implements `UnderFileSystemFactory`. `create` validates path and required credentials through `checkOSSCredentials`, then calls `OSSUnderFileSystem.createInstance`. `supportsPath` checks `Constants.HEADER_OSS`. Credential checks require access key, secret key, and endpoint properties.

## Control Flow
The factory reports support based on URI prefix but only creates a UFS when configuration contains the required OSS connection keys. Exceptions are wrapped with Guava `Throwables.propagate`.

## State And Persistence
The factory is stateless.

## Dependencies And Integration Points
It integrates the OSS module with `UnderFileSystemFactoryRegistry` and delegates actual client construction to `OSSUnderFileSystem`.

## Risks
STS mode may not need the same static credentials, but the factory-level credential check can reject creation before STS construction logic runs if the required static keys are absent.

## Test Signals
`OSSUnderFileSystemFactoryTest` verifies registry discovery for `oss://` paths but does not test credential gating or STS mode.
