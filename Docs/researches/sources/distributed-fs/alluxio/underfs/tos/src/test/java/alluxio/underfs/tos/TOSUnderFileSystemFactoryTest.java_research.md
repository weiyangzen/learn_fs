# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSUnderFileSystemFactoryTest.java

## Purpose
This test suite verifies TOS UFS factory registration, scheme support, null-path handling, and credential gating.

## Important Tests
`setUp` mocks an `InstancedConfiguration` with root TOS URI and credential properties, then obtains the factory through `UnderFileSystemFactoryRegistry`. `factory` expects the registry lookup to succeed. `createInstanceWithNullPath` expects a path-related `NullPointerException`. `supportsPath` accepts `tos://` and rejects `s3a://`, invalid strings, and null. `createInstanceWithMissingCredentials` clears access and secret keys and expects a runtime failure containing the credential error.

## Dependencies and Integration
The test relies on Alluxio registry loading, mocked configuration, and default UFS configuration wrapping.

## Signals and Gaps
The suite validates early factory behavior, not actual TOS client construction. Endpoint and region missing-credential permutations are not separately tested.
