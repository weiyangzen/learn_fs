<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/pom.xml.in -->
# sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/pom.xml.in

## Purpose
Maven POM template for the Hadoop 1 OrangeFS filesystem plugin jar.

## Important APIs, Types, And Functions
Defines group `org.apache.hadoop.fs.ofs`, artifact `orangefs-hadoop1`, jar packaging, version substituted from OrangeFS version macros, and dependencies on `hadoop-core` 1.2.1, `orangefs-jni` with matching OrangeFS version, and test-scope JUnit 4.12.

## Control Flow
No runtime control flow. Configure substitutes version placeholders before Maven builds the project.

## State And Persistence
Build metadata persists in the generated POM and Maven artifacts. It declares the dependency graph required to compile/package the adapter.

## Dependencies And Integration Points
Integrates OrangeFS JNI bindings with the Hadoop 1 `FileSystem` API. Depends on Maven repositories containing Hadoop core, OrangeFS JNI, log4j through Hadoop, and JUnit.

## Risks And Test Signals
Risks include old Hadoop 1 dependency, source compatibility constraints, version substitution drift between adapter and JNI jar, and no explicit compiler plugin beyond command-line flags in the build script. Test signals are `mvn package`, dependency resolution, unit test execution if enabled, and loading `org.apache.hadoop.fs.ofs.OrangeFileSystem` in Hadoop 1.2.1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/client/hadoop/orangefs-hadoop1/pom.xml.in -->
