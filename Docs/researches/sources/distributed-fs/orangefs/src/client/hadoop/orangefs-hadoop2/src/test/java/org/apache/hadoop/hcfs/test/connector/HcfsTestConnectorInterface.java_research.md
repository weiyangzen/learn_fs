<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorInterface.java -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorInterface.java

## Purpose

This connector source provides factory/interface glue for creating OrangeFS-backed Hadoop `FileSystem` instances in generic HCFS tests.

## Important APIs, Types, and Functions

Relevant test/API surface:

- No local `test*` methods; behavior is inherited from a Hadoop test base.

## Control Flow

Tests create or obtain a Hadoop `FileSystem` through the HCFS connector or direct OrangeFS configuration, perform filesystem operations against `ofs://` paths, assert Hadoop-visible results, and clean up generated paths in teardown hooks where present.

## State, Persistence, and Concurrency

The tests mutate live OrangeFS-backed paths and local temporary files. Persistent state is external to the test JVM, so teardown and disposable storage are important. There is no explicit concurrency testing in these files.

## Dependencies and Integration Points

They depend on JUnit 4, Hadoop test classes, the OrangeFS Hadoop adapter, JNI/native libraries, configured `core-site.xml`, and a running/mounted OrangeFS example environment.

## Risks and Test Signals

Mis-set `HCFS_TEST_CONNECTOR` environment/class property can make the test suite instantiate the wrong connector or fail reflectively. Run these tests after starting the OrangeFS and Hadoop example services; failures in setup usually indicate configuration or native-library loading problems rather than pure Java unit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/src/test/java/org/apache/hadoop/hcfs/test/connector/HcfsTestConnectorInterface.java -->
