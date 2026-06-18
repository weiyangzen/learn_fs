<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/OrangeFSMultipleVolumeTest.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/OrangeFSMultipleVolumeTest.java

## Purpose

This test validates multiple OrangeFS authority mappings. It asks Hadoop for filesystems for `ofs://localhost-orangefs:3334` and `ofs://localhost-orangefs:3335`, checks existence on each configured volume, and verifies a missing path on one volume.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testDefaultPath`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

It depends on multiple configured OrangeFS systems/mounts; it is the main signal for `fs.ofs.systems` and `fs.ofs.mntLocations` matching logic. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/OrangeFSMultipleVolumeTest.java -->
