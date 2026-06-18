# sources/distributed-fs/alluxio/underfs/web/src/test/java/alluxio/underfs/web/WebUnderFileSystemFactoryTest.java

## Purpose
This JUnit test verifies Web UFS factory discovery for HTTP and HTTPS URLs.

## Important Tests
The `factory` test asks `UnderFileSystemFactoryRegistry.find` for an HTTPS Alluxio downloads URL and an HTTP Alluxio downloads URL and expects factories for both. It asks for `httpx://path` and expects no factory.

## Dependencies and Integration
The test uses Alluxio global configuration and registry lookup, so it validates service registration and scheme matching.

## Signals and Gaps
The comment mentions `/` or `file://`, but the actual test covers HTTP/HTTPS only. The suite does not test `create`, malformed URLs, timeout configuration, or network operations.
