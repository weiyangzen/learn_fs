# sources/distributed-fs/alluxio/underfs/swift/src/test/java/alluxio/underfs/swift/SwiftUnderFileSystemFactoryTest.java

## Purpose
This JUnit test verifies that the Swift UFS factory is discoverable through Alluxio's factory registry for supported path schemes.

## Important Tests
The single `factory` test asks `UnderFileSystemFactoryRegistry.find` for a `swift://localhost/test/path` URI and expects a non-null factory. It also asks for a `file://localhost/test/path` URI and expects no Swift factory match.

## Dependencies and Integration
The test uses `Configuration.global()` and the shared UFS registry, so it validates service registration in addition to the factory's `supportsPath` logic.

## Signals and Gaps
This is a narrow registration test. It does not exercise `create`, Swift credential gating, simulation mode, or constructor failures when the target Swift container is missing.
