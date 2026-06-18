# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.0-alpha4.xml

## Purpose

This XML is the JDiff baseline for `Apache Hadoop HDFS 3.0.0-alpha4`, generated on 2017-06-30. It captures a later Hadoop 3 alpha public API snapshot for the HDFS module.

## Important APIs, Types, And Functions

The public callable surface remains `JournalNodeMXBean`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider` with 12 methods and 2 constructors. Compared with alpha2/alpha3, the package count is 43 rather than 45: disk balancer packages are present, but the datanode web DTP and erasure-code tool package declarations seen in earlier alpha snapshots are not present in this file. The important methods remain `getJournalsStatus()`, audit initialization/event logging, caller-context and token-tracking audit overloads, inode attribute retrieval by string/array/byte-array path forms, and external access-control enforcer selection.

## Control Flow And State

The file is a static XML API graph. JDiff walks package/type/member nodes to compare public API state across releases. Persisted state includes the alpha4 API name, package inventory, type inheritance, abstract flags, method signatures, constructor signatures, docs, and generation classpath.

## Dependencies And Integration Points

The generator metadata reflects Hadoop 3 alpha4 dependency updates, including SLF4J 1.7.25, Zookeeper 3.4.9, Curator 2.12.0, Kerby 1.0.0, Jetty 9, Jersey 1.19, servlet 3.1, Netty 3.10.5, HTrace 4.1, Jackson 2.7.8 components, and `hadoop-hdfs-client-3.0.0-alpha4`. Integration points are JDiff release checks plus NameNode audit, inode attribute/access-control extension, and JournalNode JMX consumers.

## Risks And Test Signals

Risk is concentrated in package inventory differences from earlier alpha baselines and in extension interface stability before the 3.0 GA line. Tests should confirm well-formed XML, `Apache Hadoop HDFS 3.0.0-alpha4` API naming, expected 43 packages and 12 methods, intentional package differences versus alpha2/alpha3, and clean JDiff output for approved compatibility expectations.
