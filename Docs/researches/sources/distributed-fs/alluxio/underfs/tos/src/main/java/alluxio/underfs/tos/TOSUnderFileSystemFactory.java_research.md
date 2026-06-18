# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSUnderFileSystemFactory.java

## Purpose
`TOSUnderFileSystemFactory` registers the `tos://` scheme and creates configured TOS UFS instances.

## APIs and Control Flow
`supportsPath` checks for non-null paths starting with `Constants.HEADER_TOS`. `create` validates the path, checks for access key, secret key, endpoint, and region, then delegates to `TOSUnderFileSystem.createInstance`. SDK `TosException` is logged and converted to `AlluxioTosException`; other exceptions are propagated.

## State, Dependencies, and Integration
The factory is stateless. It depends on Alluxio URI/config/factory interfaces, TOS property keys, Guava preconditions/throwables, and the TOS exception type. It is loaded by Alluxio's factory registry.

## Risks and Test Signals
Credential checking uses `isSet`, so empty configured values may pass initial gating and fail later. Missing credentials become propagated runtime exceptions. `TOSUnderFileSystemFactoryTest` covers registry discovery, null path, supported and unsupported schemes, and missing credentials.
