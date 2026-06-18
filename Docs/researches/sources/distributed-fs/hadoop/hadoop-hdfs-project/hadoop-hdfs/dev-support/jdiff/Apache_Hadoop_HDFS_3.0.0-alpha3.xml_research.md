# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.0-alpha3.xml

## Purpose

This XML is the public API baseline for `Apache Hadoop HDFS 3.0.0-alpha3`, generated on 2017-05-25. It tracks the HDFS module's public annotated API during the Hadoop 3 alpha release sequence.

## Important APIs, Types, And Functions

The file declares 45 packages and the same 4 public types as alpha2: `JournalNodeMXBean`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider`. Important functions are JournalNode journal status reporting, audit logger initialization and event emission, `HdfsAuditLogger` overloads that include caller context and delegation token tracking inputs, and inode attribute/access-control hooks. Package declarations include disk balancer, erasure coding tools, datanode web DTP, server, protocol, qjournal, tools, util, and web resource namespaces.

## Control Flow And State

There is no executed algorithm. The file's control structure is its XML hierarchy, and its durable state is the generated public signature baseline for alpha3. JDiff uses that tree to detect additions, removals, and signature changes. The package-level HDFS documentation continues to describe a distributed `FileSystem` with single-writer ordered byte stream semantics.

## Dependencies And Integration Points

The doclet command embeds the alpha3 build classpath, including Hadoop common/auth, HDFS client, Kerby, Jetty 9, Jersey 1.19, Jackson/JAXB, protobuf, Netty, HTrace, and related libraries. Integration points are release-time JDiff comparison and runtime extension contracts for NameNode audit, external access control, inode attributes, and JournalNode JMX.

## Risks And Test Signals

The main risks are alpha-to-alpha API churn and accidental divergence from alpha2/alpha4. Since the exposed method set is small, any method signature change is high signal. Tests should parse the XML, compare package and method counts, run JDiff against adjacent alpha XMLs, and verify audit/access-control plugin behavior in Hadoop 3 builds.
