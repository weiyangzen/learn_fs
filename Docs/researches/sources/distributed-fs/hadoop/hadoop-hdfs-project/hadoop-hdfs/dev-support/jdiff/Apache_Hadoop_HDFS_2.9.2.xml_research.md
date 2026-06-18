# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_2.9.2.xml

## Purpose

This XML is the JDiff public API snapshot for `Apache Hadoop HDFS 2.9.2`, generated on 2018-11-13. It anchors API compatibility checks for the later 2.9 maintenance release.

## Important APIs, Types, And Functions

The exposed public surface remains the compact server-extension set: `JournalNodeMXBean.getJournalsStatus()`, `AuditLogger.initialize(Configuration)`, `AuditLogger.logAuditEvent(...)`, `HdfsAuditLogger` event overloads with `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`, and `INodeAttributeProvider` lifecycle, attribute, and access-control hooks. The package inventory is the same 38-package HDFS module namespace set as 2.8.x and 2.9.1.

## Control Flow And State

The file persists the generated API signature tree and generator metadata. A JDiff run consumes it by comparing names, inheritance, abstract flags, parameters, return types, exceptions, fields, and docs against another API XML. Runtime control flow is only documented indirectly, notably audit logging's placement in NameNode critical sections.

## Dependencies And Integration Points

The metadata shows generation against Hadoop 2.9.2 module outputs with Hadoop common/auth, HDFS client, servlet/Jersey, Jackson, protobuf, Netty, SLF4J/log4j, and tracing dependencies available to the doclet. The practical integration points are release API checks, NameNode audit extension implementations, inode-attribute and access-control plugin points, and JournalNode JMX status consumers.

## Risks And Test Signals

The key risk is an unintended public API difference inside the 2.9 line. Tests should verify XML well-formedness, method count and type count, package inventory, and a clean or expected JDiff result against `Apache_Hadoop_HDFS_2.9.1.xml`. Runtime-adjacent tests should cover custom audit logger behavior and external access-control provider behavior.
