# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.3.xml

## Purpose
`Apache_Hadoop_HDFS_3.0.3.xml` is the JDiff public API descriptor for Apache Hadoop HDFS 3.0.3, generated on Mon Jun 11 04:54:00 UTC 2018. Like the other files in this directory, it is a generated compatibility baseline rather than runtime HDFS code.

The meaningful public class and method surface remains the 3.0.x audit/JMX/inode-extension set. The notable descriptor-level change from 3.0.0 through 3.0.2 is package inventory: the empty `org.apache.hadoop.hdfs.tools.federation` package entry is no longer present, reducing the package count from 44 to 43.

## Important APIs, Types, and Functions
The file lists 43 packages, 4 public class/interface entries, and 12 methods. `JournalNodeMXBean.getJournalsStatus()` remains the JournalNode JMX management hook. `AuditLogger.initialize(Configuration)` and `AuditLogger.logAuditEvent(...)` remain the public audit interface.

`HdfsAuditLogger` still provides the abstract audit logging base and overloads for caller context, user identity, and delegation-token secret manager data. `INodeAttributeProvider` still provides NameNode lifecycle, attribute lookup, and access-control-enforcer hooks through `start()`, `stop()`, `getAttributes(...)`, and `getExternalAccessControlEnforcer(...)`.

## Control Flow
The descriptor is declarative XML. The represented runtime flow is unchanged from earlier 3.0.x snapshots: JournalNode publishes journal status; NameNode configures audit and inode attribute provider extension points at startup; audit events are logged from critical NameNode operation paths; custom inode attribute providers participate in metadata and authorization evaluation.

The generation command records the doclet invocation over the HDFS Java source path with Hadoop 3.0.3 artifacts and dependencies. Compared with 3.0.0-3.0.2, dependency metadata moves to newer client libraries while the public signatures remain stable.

## State and Persistence
Persistent content is limited to the 3.0.3 API description: package list, public type entries, signatures, flags, docs, and classpath metadata. There is no runtime mutable state in the XML. The APIs described by it refer to live JournalNode status, NameNode audit context, security identities, delegation-token tracking, inode attributes, and external authorization decisions.

## Dependencies and Integration Points
JDiff `api.xsd`, `IncludePublicAnnotationsJDiffDoclet`, release-site generation, JMX, NameNode auditing, and NameNode metadata/permission extension points are the core integrations. Referenced Hadoop types include `Configuration`, `FileStatus`, `CallerContext`, `UserGroupInformation`, `DelegationTokenSecretManager`, and `INodeAttributes`.

The recorded classpath shows patch-line dependency movement: commons-net is 3.6, OkHttp is 2.7.5, and Okio is 1.6.0, while ZooKeeper remains 3.4.9, Curator remains 2.12.0, Jetty remains 9.3.19, protobuf remains 2.5.0, Netty remains 3.10.5/4.0.23, and commons-compress remains 1.4.1.

## Risks and Edge Cases
The removed empty `org.apache.hadoop.hdfs.tools.federation` package can appear as an API/package difference even though no public classes or methods were removed. Consumers that compare package inventories should decide whether empty package removal is acceptable for their compatibility policy.

The same extension-point risks remain: `AuditLogger` implementations must be fast because NameNode calls them in a critical path, and custom `INodeAttributeProvider`/access-control enforcer implementations can change authorization outcomes. Dependency metadata changes in the generation classpath can also complicate reproducibility if the descriptor is regenerated.

## Test Signals
Validation should confirm XML parseability, package count 43, class/interface count 4, and method count 12. JDiff comparison against 3.0.2 should show only generated metadata/dependency changes plus the removed empty federation package. Runtime-facing checks should cover JournalNode JMX, audit logger overload dispatch, token/caller-context logging, inode attribute provider lifecycle, and custom access-control enforcer behavior.
