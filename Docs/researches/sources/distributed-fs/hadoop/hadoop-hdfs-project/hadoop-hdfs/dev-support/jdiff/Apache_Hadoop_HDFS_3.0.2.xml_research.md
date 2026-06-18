# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.2.xml

## Purpose
`Apache_Hadoop_HDFS_3.0.2.xml` is the generated JDiff XML baseline for the public annotated HDFS API in Apache Hadoop HDFS 3.0.2, generated on Fri Apr 13 23:56:52 UTC 2018. It is a compatibility artifact for JDiff, not an implementation file.

This file records the HDFS 3.0.2 public API surface while preserving the HDFS package documentation that emphasizes distributed `FileSystem` behavior and the single-writer append model. Its body remains substantively aligned with the 3.0.0 and 3.0.1 descriptors.

## Important APIs, Types, and Functions
The descriptor contains 44 package entries, 4 public class/interface entries, and 12 public methods. `JournalNodeMXBean` exposes `getJournalsStatus()` for JournalNode JMX management. `AuditLogger` defines initialization and the required audit-event logging method.

`HdfsAuditLogger` supplies the abstract audit logger base class and overloads for plain audit records, caller context, `UserGroupInformation`, and delegation-token secret manager handling. `INodeAttributeProvider` exposes lifecycle and metadata/authorization extension methods: `start()`, `stop()`, `getAttributes(String, INodeAttributes)`, `getAttributes(String[], INodeAttributes)`, `getAttributes(byte[][], INodeAttributes)`, and `getExternalAccessControlEnforcer(...)`.

## Control Flow
The XML itself is declarative. Its implied runtime flow is that JournalNode registers management status, NameNode startup initializes audit and inode attribute provider hooks, NameNode operation handling invokes audit logging in critical sections, and inode permission/metadata resolution consults configured attribute providers and optional external enforcers.

The generation flow remains the Hadoop annotation-aware JDiff doclet over HDFS source, with HDFS, HDFS client, Hadoop common/auth/annotations, Kerberos, ZooKeeper/Curator, web stack, JSON, protobuf, Netty, and storage-related dependencies on the classpath.

## State and Persistence
The file persists the 3.0.2 API signature state as XML: names, flags, method signatures, parameters, exceptions, docs, and package inventory. It does not persist NameNode or DataNode state and has no runtime mutation path.

The described public APIs interact with operational state outside this file: JournalNode journal state, audit event contents, security identity/delegation token context, inode attributes, and custom authorization decisions.

## Dependencies and Integration Points
Integration points are JDiff `api.xsd`, Hadoop's `IncludePublicAnnotationsJDiffDoclet`, release-site generation, JMX, NameNode audit logging, and NameNode authorization/metadata extension hooks. Types referenced by the API include `Configuration`, `FileStatus`, `CallerContext`, `UserGroupInformation`, `DelegationTokenSecretManager`, `INodeAttributes`, and `INodeAttributeProvider.AccessControlEnforcer`.

The generated classpath still reflects the 3.0.0-3.0.2 dependency set, including ZooKeeper 3.4.9, Curator 2.12.0, Jetty 9.3.19, Jersey 1.19, protobuf 2.5.0, Netty 3.10.5/4.0.23, OkHttp 2.4.0, Okio 1.4.0, commons-net 3.1, and commons-compress 1.4.1.

## Risks and Edge Cases
As with the other 3.0.x patch descriptors, a stable JDiff body does not imply no runtime bug fixes or private behavior changes. Consumers should avoid using this XML as a full behavioral specification. Empty package entries can still affect compatibility reports.

Custom audit and inode-attribute implementations remain the highest-risk downstream integration points. Slow audit logging can directly affect NameNode operation latency, while incorrect attribute provider or access-control enforcer behavior can expose metadata inconsistencies or authorization regressions.

## Test Signals
Tests should verify XML parseability, stable counts of 44 packages, 4 class/interface entries, and 12 methods, and no substantive body diff against 3.0.0/3.0.1 after ignoring generated metadata. Runtime-facing coverage should exercise JournalNode status JMX, audit logger overloads including caller context and token manager cases, and custom `INodeAttributeProvider` permission/attribute behavior.
