<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml` is the Maven module descriptor for Apache Hadoop `hadoop-hdfs-nfs`. The source was read as a complete 258-line file for this report.

## Important APIs, Types, and Functions

The POM declares parent `hadoop-project` version `3.6.0-SNAPSHOT`, artifact `hadoop-hdfs-nfs`, JAR packaging, compile/provided/test dependencies, a `dist` profile using `maven-assembly-plugin`, and SpotBugs configuration pointing at the global exclude file.

## Control Flow

During Maven builds the dependency graph supplies Hadoop common/HDFS/NFS, Netty, Jetty/Jersey, commons libraries, protobuf, servlet APIs, metrics, logging, and test frameworks. The `dist` profile packages the module with the Hadoop HDFS NFS assembly descriptor.

## State and Persistence Behavior

Build outputs are persisted under Maven target directories and optional distribution artifacts. The POM does not affect runtime state except through dependency versions/scopes and packaged resources.

## Dependencies and Integration Points

This module integrates `hadoop-nfs`, `hadoop-hdfs`, `hadoop-hdfs-client`, shaded Guava, Netty, Jetty, Jersey, commons-daemon, metrics, protobuf, JUnit 5, Mockito, AssertJ, and Hadoop test jars.

## Risks and Edge Cases

Dependency scope mistakes can produce missing runtime classes or oversized artifacts. The SpotBugs configuration uses only the global exclude file, so module-specific findings must be addressed or globally justified.

## Test Signals

`mvn -pl hadoop-hdfs-project/hadoop-hdfs-nfs test`, dependency analysis, SpotBugs, and `-Pdist package` validate this descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml -->
