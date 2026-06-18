# sources/distributed-fs/alluxio/underfs/wasb/src/test/java/alluxio/underfs/wasb/WasbUnderFileSystemFactoryTest.java

## Purpose
This JUnit test verifies that the WASB module is registered for Azure Blob Storage schemes.

## Important Tests
The single `factory` test uses `UnderFileSystemFactoryRegistry.find` to assert non-null factories for `wasb://localhost/test/path` and `wasbs://localhost/test/path`, then asserts no matching factory for `alluxio://localhost/test/path`.

## Dependencies and Integration
The test uses Alluxio global configuration and the shared UFS registry, so it checks service registration rather than just calling `supportsPath` directly.

## Signals and Gaps
Coverage is limited to path support. It does not verify Hadoop Azure class configuration, account-key propagation, secure vs insecure configuration, or block-size status rewriting.
