# sources/distributed-fs/alluxio/underfs/oss/pom.xml

## Purpose
This Maven module descriptor builds the Aliyun OSS under file system implementation.

## Important APIs, Types, And Functions
The artifact is `alluxio-underfs-oss` under parent `alluxio-underfs`. It declares external dependencies on `aliyun-sdk-oss` and `commons-codec`, provided dependency on `alluxio-core-common`, a test-jar dependency for common tests, and `mockito-inline` for tests.

## Control Flow
Maven inherits most build behavior from the parent. The module configures shade and copy-rename plugins without local execution details, leaving dependency packaging and renamed artifacts to shared plugin configuration.

## State And Persistence
The POM has no runtime state. It controls dependency resolution, test classpath, and build output.

## Dependencies And Integration Points
It is listed by the parent `underfs/pom.xml` and contributes OSS classes and service-provider resources to Alluxio UFS packaging.

## Risks
OSS SDK compatibility and shaded dependency boundaries are the key risk. `mockito-inline` is needed for tests that mock final/static-adjacent SDK behavior.

## Test Signals
Successful module build compiles OSS adapter classes and the mock-heavy stream/UFS/STS tests in this subset.
