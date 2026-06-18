# sources/distributed-fs/alluxio/underfs/swift/src/main/java/alluxio/underfs/swift/SwiftUnderFileSystemFactory.java

## Purpose
`SwiftUnderFileSystemFactory` registers and constructs the Swift UFS implementation for paths beginning with Alluxio's `swift://` header.

## APIs and Control Flow
`supportsPath` returns true for non-null paths starting with `Constants.HEADER_SWIFT`. `create` validates the path, checks credentials, and returns a new `SwiftUnderFileSystem`; construction exceptions are propagated through Guava `Throwables.propagate`. `checkSwiftCredentials` accepts simulation mode without credentials; otherwise it requires password, tenant, auth URL, and user keys.

## State, Dependencies, and Integration
The factory is stateless and `@ThreadSafe`. It depends on Alluxio configuration keys, URI construction, the UFS factory interface, and Guava preconditions/throwables. It is consumed through `UnderFileSystemFactoryRegistry`.

## Risks and Test Signals
Credential checking does not require an auth method or region, leaving those to the UFS constructor. Missing credentials become a propagated `IOException` rather than a checked failure. `SwiftUnderFileSystemFactoryTest` verifies registry discovery for `swift://` and rejection of `file://`, but not credential permutations.
