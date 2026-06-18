# sources/distributed-fs/alluxio/underfs/tos/pom.xml

## Purpose
This Maven module declares Alluxio's Tinder Object Storage under file system implementation as `alluxio-underfs-tos`.

## Important Configuration
The module inherits from `alluxio-underfs` version `2.10.0-SNAPSHOT`, sets `build.path` for subproject builds, and describes the artifact as the Tinder Object Storage UFS. Runtime dependencies include `com.volcengine:ve-tos-java-sdk`, `commons-codec`, and provided `alluxio-core-common`. Tests depend on Alluxio common test jar and Mockito inline.

## Build and Integration
The build uses the shared `maven-shade-plugin` and `copy-rename-maven-plugin`, aligning it with the packaging model used by other Alluxio UFS modules. The Volcengine SDK dependency is the key external integration for all TOS client operations.

## Risks and Test Signals
Dependency versions are inherited, so module behavior depends on parent dependency management. The module name and description use "Tinder Object Storage"; any product rename must be handled consistently in docs and configuration keys. Test dependencies show the implementation is designed for mock-heavy unit tests rather than live TOS integration.
