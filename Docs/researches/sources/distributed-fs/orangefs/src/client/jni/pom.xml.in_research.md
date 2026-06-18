<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/pom.xml.in -->
# sources/distributed-fs/orangefs/src/client/jni/pom.xml.in

## Purpose

This Maven POM template builds the `orangefs-jni` Java jar that exposes OrangeFS/POSIX/stdio JNI classes to the Hadoop adapter and other Java clients.

## Important APIs, Types, and Functions

Important coordinates are `org.orangefs.usrint:orangefs-jni`; dependencies are commons-logging, log4j, and JUnit for tests. The compiler plugin is pinned to Java 5 source/target for older compatibility.

## Control Flow

Maven reads the substituted POM during package builds, compiles Java sources under `src/main/java`, resolves declared dependencies, and emits a versioned jar consumed by the OrangeFS installation or Hadoop classpath.

## State, Persistence, and Concurrency

The POM is build metadata only. It produces jar artifacts under `target/` and does not persist runtime filesystem state.

## Dependencies and Integration Points

The jar must match the native JNI shared library built from `libPVFS2POSIXJNI.c` and `libPVFS2STDIOJNI.c`, and its version is substituted from OrangeFS build variables.

## Risks and Test Signals

Java/native signature drift is the key risk: Maven can build Java while native methods fail at runtime. Test by running JNI smoke tests that load the native library and call stat/open/read/write.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/jni/pom.xml.in -->
