# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.0-alpha2.xml

## Purpose

This XML is the JDiff baseline for `Apache Hadoop HDFS 3.0.0-alpha2`, generated on 2017-01-20. It captures the public annotated HDFS module API during the Hadoop 3 alpha cycle and is used to track compatibility while new server namespaces were being introduced.

## Important APIs, Types, And Functions

The callable public types are the same 4 extension/management types seen in 2.8/2.9: `JournalNodeMXBean`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider`, with the same 12-method set. The package list expands to 45 packages, adding Hadoop 3-era namespaces such as datanode web DTP, disk balancer packages, and erasure-coding tools. This makes the package inventory itself an important part of the API baseline even though most added packages do not expose public types in this XML.

## Control Flow And State

The XML is static release metadata and public signature state. JDiff consumers compare it to previous or later XML snapshots to identify package/type/member changes. It records abstractness, constructors, method overloads, params, docs, and release identity but performs no I/O or state mutation itself.

## Dependencies And Integration Points

The generation command shows the Hadoop 3 build context: Java 8, Kerby Kerberos dependencies, Jetty 9, Jersey 1.19, commons-configuration2, HDFS client 3.0.0-alpha2, HTrace core4, protobuf, Netty, and common Hadoop artifacts. Runtime-facing contracts include JournalNode JMX, NameNode audit logging, inode attribute providers, and access-control enforcers. Release-facing integration is the JDiff XML comparison pipeline.

## Risks And Test Signals

Alpha snapshots carry extra risk of public API churn. The package inventory should be checked carefully because new package declarations can affect compatibility reporting even without public classes. Test signals include XML parse success, expected 45 packages and 12 methods, comparison against alpha3/alpha4, and targeted tests for audit logging and access-control extension behavior under Hadoop 3 dependencies.
