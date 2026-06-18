# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/test/java/org/apache/hadoop/fs/http/client/TestHttpFSFileSystemLocalFileSystem.java

## Purpose
This subclass runs the base HttpFS client tests with a local filesystem backend (`file:///`) rather than HDFS.

## Important APIs, Types, and Functions
It extends `BaseTestHttpFSWith`. Static initialization creates a local test root and stores `PATH_PREFIX`. It returns prefixed test directories, `file:///` as the proxied URI, and a minimal configuration with `fs.defaultFS`. `addPrefix` uses `Path.mergePaths`. `testSetPermission` is overridden for Windows to skip sticky-bit checks unsupported by local FS.

## Control Flow
Inherited operations run, but many base methods early-return when `isLocalFS()` is true. Paths are prefixed to keep local file operations under the test root.

## State and Persistence
Creates local test directories and files under Hadoop test temp locations. No HDFS cluster state is used.

## Dependencies and Integration Points
It validates HttpFS behavior when `FileSystemAccessService` proxies a local filesystem, giving coverage for operations shared between local and HDFS backends.

## Risks
Coverage is intentionally incomplete because HDFS-only features are skipped. Local filesystem checksum side files are called out by the base batched-listing test and can make direct listing comparisons invalid.

## Test Signals
This class signals which parts of HttpFS are backend-independent and guards Windows-specific permission behavior.
