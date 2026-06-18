<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSPerformanceIOTests.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSPerformanceIOTests.java

## Purpose

This class tests OrangeFS stream buffering behavior by writing around `DEFAULT_OFS_FILE_BUFFER_SIZE` and checking when data spills to the filesystem.

## Important APIs, Types, and Functions

Relevant test/API surface:

- `testBufferSpill`

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

The assertions depend on buffer-size defaults and a live filesystem's length visibility. It is a useful signal for output-stream flush/spill behavior. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/unit/HCFSPerformanceIOTests.java -->
