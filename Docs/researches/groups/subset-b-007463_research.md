# subset-b-007463 research

This grouped report covers Hadoop HDFS JDiff API descriptors under `sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff`. Each section preserves the original source path so the reconciliation step can split it into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.0.xml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.0.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.1.xml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.2.xml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.2.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.3.xml -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.0.3.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.0.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.0.xml

## Purpose
`Apache_Hadoop_HDFS_3.1.0.xml` is the generated JDiff public API snapshot for Apache Hadoop HDFS 3.1.0, generated on Fri Mar 30 00:27:59 UTC 2018. It records the 3.1.0 public annotated API for compatibility checks and site output.

Compared with the 3.0.x descriptors, this file substantially expands the public surface for provided-storage block aliasing. It introduces public APIs around in-memory alias maps, file regions, abstract alias map readers/writers, and LevelDB/text-backed alias map implementations, while retaining the JournalNode JMX, NameNode audit, and `INodeAttributeProvider` APIs.

## Important APIs, Types, and Functions
The descriptor contains 46 packages, 10 public class/interface entries, 47 methods, constructors, and public fields. `org.apache.hadoop.hdfs.server.aliasmap.InMemoryAliasMap` implements `InMemoryAliasMapProtocol` and `Configurable`, with `setConf()`, `getConf()`, static `init(Configuration, String)`, `list(Optional)`, `read(Block)`, `write(Block, ProvidedStorageLocation)`, `getBlockPoolId()`, `close()`, protobuf conversion helpers for `ProvidedStorageLocation` and `Block`, and `toProtoBufBytes(...)` overloads.

`org.apache.hadoop.hdfs.server.common.BlockAlias` defines `getBlock()`. `FileRegion` implements `BlockAlias` and models a provided block as a path, offset, length, generation stamp, and optional nonce via constructors and `getBlock()`, `getProvidedStorageLocation()`, `equals()`, and `hashCode()`. `BlockAliasMap` is an abstract base for alias map storage with `getReader(...)`, `getWriter(...)`, `refresh()`, and `close()`. `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap` implement configurable storage backends, each exposing reader/writer/refresh/close methods and a public static `LOG`; the text backend also has `blockPoolIDFromFileName(Path)` and `fileNameFromBlockPoolID(String)`.

The previous APIs remain: `JournalNodeMXBean.getJournalsStatus()`, `AuditLogger`, `HdfsAuditLogger` overloads, and `INodeAttributeProvider` lifecycle, attribute, and access-control methods.

## Control Flow
The XML is declarative, but it describes several runtime flows. Provided-storage clients initialize `InMemoryAliasMap` for a block pool, read/write block-to-`ProvidedStorageLocation` mappings, list with optional markers, and serialize/deserialize blocks and locations through protobuf bytes. `BlockAliasMap` consumers request readers and writers for a block pool, refresh backing stores, and close resources.

File region aliasing flows through `FileRegion`: a block maps to a `ProvidedStorageLocation` describing file path, offset, length, and identity data. `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap` provide persistence backends selected by configuration. Existing NameNode flows for audit logging and inode attribute substitution remain as in 3.0.x.

## State and Persistence
The XML persists the API state for 3.1.0. The APIs it describes introduce real persistence concepts outside the XML: alias maps maintain block-pool-scoped mappings from HDFS blocks to provided-storage locations; LevelDB and text implementations persist those mappings in backing stores; readers/writers expose lifecycle and refresh semantics.

`InMemoryAliasMap` maintains configuration, block pool ID, and map contents in runtime service state while providing protobuf conversion boundaries. Audit and inode-provider APIs continue to operate over NameNode operation context, security state, inode attributes, and permission-enforcement decisions.

## Dependencies and Integration Points
The descriptor integrates with JDiff `api.xsd`, Hadoop's annotation-aware JDiff doclet, release-site tooling, and API compatibility checks. Provided-storage APIs integrate with `Block`, `ProvidedStorageLocation`, `Path`, `Configuration`, `Configurable`, `Optional`, protobuf parsing (`InvalidProtocolBufferException`), `IOException`, LevelDB-backed storage, text-file storage, and SLF4J logging.

Generation metadata records Hadoop 3.1.0 dependencies such as ZooKeeper 3.4.9, Curator 2.12.0, Jetty 9.3.19, Jersey 1.19, protobuf 2.5.0, Netty 3.10.5/4.0.52, OkHttp 2.7.5, Okio 1.6.0, commons-net 3.6, and commons-compress 1.4.1.

## Risks and Edge Cases
The 3.1.0 alias-map surface is broader and more persistence-sensitive than the 3.0.x API. Risks include malformed protobuf bytes, inconsistent block pool IDs, stale reader/writer views without `refresh()`, LevelDB or text backend corruption, and file-name/block-pool-ID encoding mismatches in `TextFileRegionAliasMap`.

Public exposure of storage backend classes and static `LOG` fields can make compatibility checks sensitive to implementation details. Existing risks remain for slow audit logging in NameNode critical sections and for custom inode attribute providers that alter authorization semantics.

## Test Signals
JDiff validation should confirm XML well-formedness, 46 packages, 10 class/interface entries, and 47 methods/constructors/fields. API comparison against 3.0.3 should show the new alias-map packages and types as additions. Runtime-facing tests should cover alias map initialization per block pool, read/write/list marker behavior, protobuf round trips for `Block` and `ProvidedStorageLocation`, `FileRegion` equality/hash behavior, LevelDB and text backend reader/writer/refresh/close lifecycles, text file naming helpers, JournalNode JMX, and audit/inode-provider extension behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.0.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.1.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.1.xml

## Purpose
`Apache_Hadoop_HDFS_3.1.1.xml` is the generated JDiff descriptor for Apache Hadoop HDFS 3.1.1, generated on Thu Aug 02 05:10:01 UTC 2018. It records the public annotated HDFS API for a 3.1.x patch release and supports compatibility reporting.

After ignoring generated metadata, the public API body is substantively aligned with the 3.1.0 descriptor: the provided-storage alias-map surface remains present, and the JournalNode JMX, NameNode audit, and inode attribute provider APIs remain stable.

## Important APIs, Types, and Functions
The file lists 46 packages, 10 public class/interface entries, and 47 methods/constructors/fields. `InMemoryAliasMap` remains the public in-memory alias map service for block-pool-scoped mappings, with configuration, initialization, list/read/write, close, and protobuf conversion methods.

`BlockAlias`, `FileRegion`, `BlockAliasMap`, `LevelDBFileRegionAliasMap`, and `TextFileRegionAliasMap` remain the provided-storage mapping abstractions and storage implementations. `JournalNodeMXBean`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider` retain the same public contracts as 3.1.0.

## Control Flow
The XML represents, but does not execute, the same 3.1.x flows: JDiff doclet generation from annotated Java sources; alias-map initialization for a block pool; alias-map reads/writes/lists and serialization boundaries; reader/writer acquisition from `BlockAliasMap` implementations; backend refresh and close; JournalNode JMX status exposure; NameNode audit event emission; and inode attribute/access-control extension calls.

Because the API body matches 3.1.0, this descriptor mainly serves to verify patch-release public compatibility while allowing runtime implementation and dependency fixes elsewhere in Hadoop.

## State and Persistence
The persisted state is the XML API baseline: package inventory, public type names, signatures, flags, docs, and generation metadata. The APIs represented by it maintain or access runtime/persistent state outside the XML: alias maps in memory, LevelDB, or text files; block-pool IDs; file-region mappings; NameNode audit event context; and inode authorization/attribute overlays.

## Dependencies and Integration Points
Integration points include JDiff `api.xsd`, Hadoop public-annotation doclet, provided-storage APIs (`Block`, `ProvidedStorageLocation`, `Path`, `Optional`, protobuf exceptions), configurable LevelDB/text alias map backends, SLF4J, JMX, and NameNode security/audit extension types.

The recorded dependency set follows the early 3.1.x line: ZooKeeper 3.4.9, Curator 2.12.0, Jetty 9.3.19, Jersey 1.19, protobuf 2.5.0, Netty 3.10.5/4.0.52, OkHttp 2.7.5, Okio 1.6.0, commons-net 3.6, and commons-compress 1.4.1.

## Risks and Edge Cases
A stable JDiff descriptor should not be mistaken for proof that alias-map persistence behavior is unchanged. Implementation details such as LevelDB schema, text delimiter handling, refresh semantics, and protobuf compatibility can change without altering public signatures.

The alias-map APIs expose checked `IOException` and protobuf parse failure paths; callers need to treat corrupt bytes, missing block pools, and backend unavailability as normal failure modes. Audit logger latency and inode-provider authorization risks remain unchanged.

## Test Signals
Validation should check XML well-formedness, 46 package entries, 10 class/interface entries, 47 public methods/constructors/fields, and no substantive body diff from 3.1.0 after excluding generation metadata. Runtime tests should exercise `InMemoryAliasMap` initialization/read/write/list/close, protobuf conversion failures and successes, `FileRegion` identity semantics, LevelDB/text reader and writer lifecycle, text filename conversion helpers, JournalNode JMX status, and NameNode audit/inode-provider extension behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.2.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.2.xml

## Purpose
`Apache_Hadoop_HDFS_3.1.2.xml` is the JDiff public API snapshot for Apache Hadoop HDFS 3.1.2, generated on Tue Jan 29 03:49:43 UTC 2019. It preserves the 3.1.2 public annotated HDFS API for compatibility analysis.

The API body remains substantively aligned with 3.1.0 and 3.1.1: provided-storage alias-map APIs are present, and the existing JournalNode JMX, NameNode audit, and inode attribute provider extension points remain stable.

## Important APIs, Types, and Functions
The descriptor contains 46 package entries, 10 class/interface entries, and 47 methods/constructors/fields. Provided-storage APIs include `InMemoryAliasMap`, `BlockAlias`, `FileRegion`, abstract `BlockAliasMap`, `LevelDBFileRegionAliasMap`, and `TextFileRegionAliasMap`, with read/write/list, reader/writer, refresh, close, protobuf conversion, file-region, and block-pool file-name helper methods.

Existing management and NameNode extension APIs remain `JournalNodeMXBean.getJournalsStatus()`, `AuditLogger.initialize(...)`, `AuditLogger.logAuditEvent(...)`, `HdfsAuditLogger` overloads with caller/security/token context, and `INodeAttributeProvider` lifecycle, attribute, and external access-control enforcer hooks.

## Control Flow
Control flow is represented as public API contracts. Provided-storage mappings flow from initialization to block-pool-scoped read/write/list operations, through protobuf serialization, into `BlockAliasMap` reader/writer backends, and through refresh/close lifecycle calls. File regions encode block-to-path/offset/length mappings for provided storage.

The JDiff generation flow remains annotation-aware source scanning under the HDFS source tree, producing XML for the release site and compatibility tooling. Runtime audit and inode provider flows remain NameNode startup initialization, operation-time audit calls, and permission/attribute resolution hooks.

## State and Persistence
This XML persists only API metadata. The described APIs handle persistent alias-map state in LevelDB or text files, transient in-memory alias map service state, block pool IDs, protobuf-encoded block/location records, file-region identity, and backend resource lifecycles.

NameNode extension APIs continue to interact with audit event state, caller/security context, delegation-token secret-manager data, inode attributes, and authorization decisions. None of that state is stored in this XML.

## Dependencies and Integration Points
JDiff `api.xsd`, Hadoop's public-annotation doclet, HDFS provided-storage classes, Hadoop `Configuration`/`Configurable`, protobuf exceptions, `Path`, `Optional`, SLF4J, LevelDB, text-file storage, JMX, and NameNode audit/security classes are the key integrations.

The generated classpath records patch-line dependency updates compared with 3.1.0/3.1.1: ZooKeeper is 3.4.13, Curator remains in the 2.x line, Jetty is 9.3.24, commons-compress is 1.18, Netty remains 3.10.5/4.0.52, OkHttp remains 2.7.5, Okio remains 1.6.0, and commons-net remains 3.6.

## Risks and Edge Cases
Dependency upgrades recorded in the descriptor can affect reproducibility and runtime behavior even when public APIs remain unchanged. In particular, storage backend behavior, compression handling, and web/JMX stack behavior can move independently of JDiff signatures.

Alias-map risks remain: corrupt protobuf data, inconsistent block pool IDs, stale refreshed state, backend close ordering, LevelDB/text storage failures, and filename conversion edge cases. Audit logging and inode-provider extension points remain sensitive because they run in NameNode security and metadata paths.

## Test Signals
Validation should confirm XML well-formedness, counts of 46 packages, 10 class/interface entries, and 47 methods/constructors/fields, and no substantive API body diff from 3.1.0/3.1.1 after generated metadata is ignored. Runtime-facing tests should cover alias-map persistence across LevelDB/text backends, protobuf round-trip and corruption paths, block-pool isolation, refresh and close behavior, text file naming helpers, JournalNode JMX, audit logger overloads, and inode-provider authorization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.2.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.3.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.3.xml

## Purpose
`Apache_Hadoop_HDFS_3.1.3.xml` is the generated JDiff public API descriptor for Apache Hadoop HDFS 3.1.3, generated on Thu Sep 12 04:55:36 UTC 2019. It captures the public annotated HDFS API for compatibility comparison at the end of the 3.1.x line represented here.

The descriptor retains the provided-storage alias-map surface introduced in 3.1.0 and the older JournalNode JMX, NameNode audit, and inode attribute provider APIs. Compared with 3.1.2, the meaningful API-body difference is in `HdfsAuditLogger`: the overload of `logAuditEvent(...)` that includes `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager` is marked `abstract="true"` in this file, whereas it was `abstract="false"` in 3.1.0 through 3.1.2.

## Important APIs, Types, and Functions
The descriptor lists 46 packages, 10 public class/interface entries, and 47 methods/constructors/fields. The provided-storage set remains `InMemoryAliasMap`, `BlockAlias`, `FileRegion`, `BlockAliasMap`, `LevelDBFileRegionAliasMap`, and `TextFileRegionAliasMap`, covering block-pool initialization, list/read/write, protobuf conversion, file-region identity, reader/writer access, refresh, close, LevelDB/text backends, and text block-pool filename helpers.

`JournalNodeMXBean.getJournalsStatus()` remains the JournalNode management API. `AuditLogger` remains the base audit interface. `HdfsAuditLogger` remains an abstract base class, but the caller-context overload is now abstract in the XML, increasing implementation requirements for subclasses if reflected in source/binary compatibility. `INodeAttributeProvider` remains the NameNode metadata and authorization extension point.

## Control Flow
The XML itself is declarative. The described provided-storage flow is unchanged: initialize alias maps for a block pool, map `Block` instances to `ProvidedStorageLocation`, serialize/deserialize records, obtain readers/writers from configured backends, refresh backend state, and close resources. LevelDB and text implementations provide concrete persistence strategies.

For audit logging, the 3.1.3 descriptor implies a stricter subclass dispatch path: implementations of `HdfsAuditLogger` may need to provide the caller-context-aware overload directly rather than inheriting a concrete bridge. NameNode still invokes audit logging during operation handling, where latency and correctness matter.

## State and Persistence
The persisted state in this file is the 3.1.3 public API signature and documentation snapshot. The described APIs manage external state such as in-memory alias maps, LevelDB/text alias-map persistence, block pool IDs, protobuf records, file-region mappings, JournalNode journal status, NameNode audit event context, delegation-token tracking, inode attributes, and external access-control decisions.

The XML has no mutable runtime state. Changes in abstractness are nevertheless compatibility state: they affect what downstream subclasses must implement and what compatibility tools report.

## Dependencies and Integration Points
Integrations include JDiff `api.xsd`, Hadoop's `IncludePublicAnnotationsJDiffDoclet`, HDFS provided-storage classes (`Block`, `ProvidedStorageLocation`, `FileRegion`, alias maps), Hadoop configuration, protobuf, LevelDB/text storage, SLF4J, JMX, NameNode audit/security classes, and inode permission extension APIs.

The generation classpath records later 3.1.x dependency movement: ZooKeeper 3.4.13, Curator 2.13.0, Jetty 9.3.24, commons-compress 1.18, Guava 27.0-jre plus split Guava support artifacts, Netty 3.10.5/4.0.52, OkHttp 2.7.5, Okio 1.6.0, commons-net 3.6, and Yetus audience annotations.

## Risks and Edge Cases
The `HdfsAuditLogger` abstractness change is the highest compatibility risk in this descriptor. Downstream subclasses that relied on the previously concrete caller-context overload could fail compilation or compatibility checks if the XML reflects the source contract. This is especially sensitive because audit logging runs in NameNode operation paths.

Provided-storage risks remain: corrupt protobuf records, block-pool naming conflicts, stale reader/writer state, backend failure during refresh/close, LevelDB or text storage corruption, and semantic mismatch between `FileRegion` equality and storage identity. The larger dependency movement in 3.1.3 also means runtime regressions may appear without additional public API changes.

## Test Signals
Validation should confirm XML well-formedness, counts of 46 packages, 10 class/interface entries, and 47 public methods/constructors/fields. A focused diff against 3.1.2 should flag the `HdfsAuditLogger.logAuditEvent(... CallerContext ...)` abstractness change plus generated dependency metadata. Runtime-facing tests should include subclass compatibility for `HdfsAuditLogger`, audit overload dispatch, alias map read/write/list across in-memory, LevelDB, and text backends, protobuf round trips and parse failures, block-pool file naming helpers, backend refresh/close semantics, JournalNode JMX status, and custom `INodeAttributeProvider` authorization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.1.3.xml -->
