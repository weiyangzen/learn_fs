<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsFileSystemTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsFileSystemTest.java

## Purpose

This is the main live HCFS behavior test suite for the OrangeFS Hadoop adapter. It exercises encoded paths, tolerant recursive mkdirs, owner lookup, text IO, permission changes, directory listing/deletion, file IO, seek/available reads, and permission mutation.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testEncodedPaths`
- `testTolerantMkdirs`
- `testOwner`
- `testTextWriteAndRead`
- `testPermissions`
- `testZDirs`
- `testFiles`
- `testFileIO`
- `testPermissionsChanging`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

It requires a live configured OrangeFS filesystem and can leave state unless teardown succeeds. It provides the strongest functional signal for filesystem compatibility. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HcfsFileSystemTest.java -->
