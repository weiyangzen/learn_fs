# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.0.xml

## Purpose
`Apache_Hadoop_HDFS_3.0.0.xml` is the JDiff XML snapshot for the public annotated API surface of Apache Hadoop HDFS 3.0.0, generated on Fri Dec 08 19:46:31 UTC 2017 by the `IncludePublicAnnotationsJDiffDoclet`. It is not runtime HDFS code; it is an API contract artifact consumed by JDiff/site tooling to compare public classes, interfaces, methods, constructors, fields, package names, documentation, and signature metadata across Hadoop releases.

The package-level documentation for `org.apache.hadoop.hdfs` describes HDFS as a distributed `FileSystem` implementation modeled loosely after GFS, with an explicit single-writer append stream model. Most listed packages are empty placeholders in this XML, but they still form part of the package inventory that API compatibility tooling can compare.

## Important APIs, Types, and Functions
The meaningful public entries are compact: 44 packages, 4 public class/interface entries, and 12 methods. `org.apache.hadoop.hdfs.qjournal.server.JournalNodeMXBean` exposes `getJournalsStatus()` for JMX-visible JournalNode journal formatting/status information. `org.apache.hadoop.hdfs.server.namenode.AuditLogger` defines `initialize(Configuration)` and the seven-parameter `logAuditEvent(...)` contract used by NameNode audit logging.

`org.apache.hadoop.hdfs.server.namenode.HdfsAuditLogger` extends the audit API with overloads that include `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager` for token tracking and caller-context-aware audit entries. `org.apache.hadoop.hdfs.server.namenode.INodeAttributeProvider` is an extension point for NameNode metadata overlays, with `start()`, `stop()`, three `getAttributes(...)` variants over string paths, path elements, and byte components, plus `getExternalAccessControlEnforcer(...)` for replacing permission enforcement behavior.

## Control Flow
Runtime control flow is represented indirectly through API documentation, not executable XML behavior. The documented flow is: JournalNode services publish status through `JournalNodeMXBean`; NameNode startup initializes configured `AuditLogger` and `INodeAttributeProvider` implementations; NameNode critical sections invoke audit logging quickly for each operation; permission and metadata lookup paths can call `INodeAttributeProvider.getAttributes(...)` and optionally delegate to a custom access-control enforcer.

The JDiff generation flow is encoded in the command-line comment: the doclet runs against `hadoop-hdfs/src/main/java`, with Hadoop HDFS, HDFS client, Hadoop common, annotations, auth, Kerberos, ZooKeeper/Curator, servlet/Jersey, Jackson, protobuf, Netty, and other dependencies on the classpath. The resulting XML becomes the release baseline for later compatibility comparison.

## State and Persistence
This file persists the release's public API state as XML: package names, class/interface abstract/static/final/visibility/deprecation flags, method return types, parameters, exceptions, docs, and the generation classpath. It has no mutable runtime state and no HDFS filesystem persistence behavior of its own.

The APIs described by the XML do touch runtime state: JournalNode journal status, NameNode audit event records, delegation-token tracking IDs, caller context, inode attributes, and permission-enforcement decisions. Those effects live in the implementation classes outside this generated descriptor.

## Dependencies and Integration Points
The descriptor depends on JDiff schema `api.xsd` and `jdversion="1.0.9"`. It integrates with Hadoop's public-annotation doclet, Maven release artifacts, and generated site reports. Runtime integration points represented by the APIs include JMX for `JournalNodeMXBean`, NameNode audit logging, Hadoop `Configuration`, `FileStatus`, `CallerContext`, `UserGroupInformation`, and HDFS delegation token secret management.

The generation classpath records 3.0.0-era dependencies, including ZooKeeper 3.4.9, Curator 2.12.0, Jetty 9.3.19, Jersey 1.19, Jackson 1.9/2.7 components, protobuf 2.5.0, Netty 3.10.5 and 4.0.23, OkHttp 2.4.0, Okio 1.4.0, commons-net 3.1, and commons-compress 1.4.1.

## Risks and Edge Cases
Because this is a generated compatibility baseline, stale or partially generated XML can cause false API compatibility conclusions. Empty package entries matter: removing an empty package in a later release may show a package inventory difference even without changed classes. The `AuditLogger.logAuditEvent(...)` documentation says calls occur in a critical NameNode section and must return quickly; custom implementations can harm NameNode latency if they block on I/O or remote services.

`INodeAttributeProvider` and its external access-control enforcer are high-risk extension points because they can alter metadata and authorization behavior. Compatibility checks should treat changes in method abstractness, parameter order, or return type as source/binary compatibility issues for downstream implementations.

## Test Signals
Useful validation signals are XML well-formedness, successful JDiff parsing against `api.xsd`, stable counts of 44 packages, 4 public class/interface entries, and 12 methods, and a clean comparison against adjacent 3.0.1/3.0.2 baselines aside from generation metadata. Runtime-facing tests should cover JournalNode JMX status exposure, custom audit logger initialization and low-latency event logging, caller-context/token tracking audit paths, and custom `INodeAttributeProvider` metadata and permission-enforcer behavior.
