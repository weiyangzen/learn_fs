<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/pom.xml.in -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/pom.xml.in

## Purpose

This Maven POM template builds the `orangefs-hadoop2` jar that registers OrangeFS as a Hadoop 2 `FileSystem` and `AbstractFileSystem` implementation. Autoconf substitutes the OrangeFS version into the project and JNI dependency versions.

## Important APIs, Types, and Functions

Important coordinates are `org.apache.hadoop.fs.ofs:orangefs-hadoop2`, dependency `org.apache.hadoop:hadoop-common:2.7.2`, dependency `org.orangefs.usrint:orangefs-jni`, and test dependencies on JUnit plus Hadoop test APIs.

## Control Flow

Maven reads the substituted POM during package builds, compiles Java sources under `src/main/java`, resolves declared dependencies, and emits a versioned jar consumed by the OrangeFS installation or Hadoop classpath.

## State, Persistence, and Concurrency

The POM is build metadata only. It produces jar artifacts under `target/` and does not persist runtime filesystem state.

## Dependencies and Integration Points

Maven resolution must find the matching `orangefs-jni` version and Hadoop 2.7.2 artifacts. The build script supplies Java 7 source/target compiler flags externally.

## Risks and Test Signals

The test dependency `hadoop-test:1.0.0` is from an older Hadoop line and may be fragile with Hadoop 2.7.2. Test by building with and without skipped tests and by loading the jar in Hadoop's classpath.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop2/pom.xml.in -->
