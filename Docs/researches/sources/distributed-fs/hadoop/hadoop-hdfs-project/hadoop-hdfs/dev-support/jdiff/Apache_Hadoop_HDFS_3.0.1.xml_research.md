# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.1.xml

## Purpose
`Apache_Hadoop_HDFS_3.0.1.xml` is the JDiff public API snapshot for Apache Hadoop HDFS 3.0.1, generated on Fri Mar 16 23:30:00 UTC 2018. It preserves the HDFS 3.0.1 public API contract for release-to-release comparison and site documentation.

The substantive API surface is the same shape as the 3.0.0 baseline after the generated header: a small set of public HDFS management, audit, and NameNode extension APIs plus a broad package inventory. The XML therefore acts primarily as a regression guard that confirms 3.0.1 did not intentionally widen or shrink the HDFS public annotated API.

## Important APIs, Types, and Functions
The file lists 44 packages, 4 public class/interface entries, and 12 methods. `JournalNodeMXBean.getJournalsStatus()` remains the JMX-facing JournalNode status hook. `AuditLogger.initialize(Configuration)` and `AuditLogger.logAuditEvent(...)` remain the core NameNode audit interface.

`HdfsAuditLogger` remains an abstract class implementing `AuditLogger`, with a basic seven-parameter log method and overloads carrying `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`. `INodeAttributeProvider` remains the NameNode extension point for lifecycle (`start()`, `stop()`), attribute substitution (`getAttributes(...)` overloads), and external access-control enforcement.

## Control Flow
No executable control flow lives in this XML. It models the same integration flow as 3.0.0: generated JDiff tooling reflects source annotations into XML; JournalNode status is exported through JMX; NameNode initializes audit and inode attribute providers; audit events are emitted inside critical NameNode operation paths; custom attribute providers can participate in path and permission resolution.

The command-line comment records the generation process and dependency resolution for Hadoop 3.0.1. Since the API body after metadata is stable against 3.0.0 and 3.0.2, compatibility control flow should treat this as a patch-release baseline rather than a feature expansion.

## State and Persistence
The persisted state is the 3.0.1 public API descriptor: package names, type flags, method signatures, parameters, exceptions, deprecation markers, and Javadoc text. There is no mutable state in the XML. Runtime state represented by the described APIs includes JournalNode journal formatting/status information, NameNode audit event context, security token tracking, and inode attribute/access-control overlays.

## Dependencies and Integration Points
The XML depends on JDiff `api.xsd` and the Hadoop public-annotation JDiff doclet. Runtime integration points remain JMX, Hadoop `Configuration`, `FileStatus`, `CallerContext`, `UserGroupInformation`, delegation-token secret management, and NameNode permission checking.

The recorded classpath is still the early 3.0.x line, including ZooKeeper 3.4.9, Curator 2.12.0, Jetty 9.3.19, Jersey 1.19, protobuf 2.5.0, Netty 3.10.5/4.0.23, OkHttp 2.4.0, Okio 1.4.0, commons-net 3.1, and commons-compress 1.4.1.

## Risks and Edge Cases
The main risk is assuming a patch release's runtime behavior from an unchanged public API descriptor. This XML can prove public signature stability, but it does not capture private implementation changes. Empty packages remain significant for JDiff comparisons, including `org.apache.hadoop.hdfs.tools.federation`, which is still present in this baseline.

Downstream risks are the same as 3.0.0: audit loggers are invoked in latency-sensitive NameNode paths, and inode attribute/access-control extensions can change authorization semantics. Compatibility tooling should verify that method abstractness and overload signatures remain stable for custom subclasses.

## Test Signals
Validation should confirm well-formed XML, successful JDiff consumption, and stable counts of 44 packages, 4 class/interface entries, and 12 methods. Diffing the API body against 3.0.0 and 3.0.2 should show no substantive changes beyond release metadata. Runtime-oriented signals include JournalNode JMX visibility, audit logger initialization and overload dispatch, token/caller-context audit coverage, and NameNode authorization behavior with custom `INodeAttributeProvider` implementations.
