# subset-b-007464 research

This grouped report covers the six Hadoop HDFS JDiff XML snapshots assigned to `subset-b-007464`. Each section is source-tree aligned and can be split directly into the mapped per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.0.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.0.xml

## Purpose

`Apache_Hadoop_HDFS_3.2.0.xml` is a JDiff API baseline generated for `Apache Hadoop HDFS 3.2.0` on 2019-01-08. It is not runtime code; it is a machine-readable public API inventory emitted by `org.apache.hadoop.classification.tools.IncludePublicAnnotationsJDiffDoclet` from the HDFS Java source tree. The file is used by Hadoop's compatibility tooling to compare public HDFS APIs between releases and to detect source or binary API drift. Its package preamble also preserves the high-level HDFS contract: HDFS is a distributed implementation of `org.apache.hadoop.fs.FileSystem`, loosely modeled after GFS, but with one writer per file and ordered byte-stream append semantics.

The snapshot declares 45 HDFS packages, most of them empty in this public API slice. The substantive exported surface is concentrated in JournalNode JMX status, provided-storage alias maps, block alias abstractions, NameNode audit logging, and `INodeAttributeProvider` extension hooks.

## Important APIs, Types, and Functions

The public management surface includes `org.apache.hadoop.hdfs.qjournal.server.JournalNodeMXBean#getJournalsStatus()`, returning a `String` status summary for JournalNode journals, including format status.

The provided-storage alias map surface centers on `org.apache.hadoop.hdfs.server.aliasmap.InMemoryAliasMap`, which implements `InMemoryAliasMapProtocol` and `Configurable`. It exposes configuration accessors, static `init(Configuration, String)` construction for a block pool, paginated `list(Optional)` returning `InMemoryAliasMapProtocol.IterationResult`, point `read(Block)`, `write(Block, ProvidedStorageLocation)`, `getBlockPoolId()`, `close()`, and protobuf conversion helpers for `ProvidedStorageLocation` and `Block`. In this 3.2.0 baseline the protobuf parse helpers throw `com.google.protobuf.InvalidProtocolBufferException`.

Provided block metadata is represented by `BlockAlias#getBlock()` and `FileRegion`, a `BlockAlias` implementation that maps an HDFS `Block` to a `ProvidedStorageLocation`. `FileRegion` has constructors from block id/path/offset/length/generation-stamp variants or from `(Block, ProvidedStorageLocation)`, plus `getBlock()`, `getProvidedStorageLocation()`, `equals(Object)`, and `hashCode()`.

Persistent alias-map abstraction is modeled by abstract `BlockAliasMap`, which provides `getReader(Reader.Options, blockPoolID)`, `getWriter(Writer.Options, blockPoolID)`, `refresh()`, and `close()`. Concrete public implementations are `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap`, both `Configurable`, both exposing reader/writer acquisition, refresh, close, and public static `LOG` fields. `TextFileRegionAliasMap` also publishes filename conversion helpers `blockPoolIDFromFileName(Path)` and `fileNameFromBlockPoolID(String)`.

The NameNode audit surface includes `AuditLogger#initialize(Configuration)` and `AuditLogger#logAuditEvent(boolean, String, InetAddress, String, String, String, FileStatus)`. `HdfsAuditLogger` extends this with overloaded audit methods carrying `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`; in 3.2.0 the caller-context overload is concrete while the token-tracking overload without caller context is abstract. `INodeAttributeProvider` is an abstract NameNode extension point with `start()`, `stop()`, path-based `getAttributes` overloads, and `getExternalAccessControlEnforcer(...)` for replacing or wrapping permission checks.

## Control Flow

As a JDiff file, parse flow is declarative: the root `<api>` names the release, lists packages, and nests `<class>`, `<interface>`, `<constructor>`, `<method>`, `<field>`, `<param>`, `<exception>`, and `<doc>` elements. JDiff consumers compare these declarations against another release snapshot rather than executing them.

The HDFS API flow captured by the declarations is more operational. Provided-storage clients initialize an `InMemoryAliasMap` with Hadoop `Configuration` and a block pool id, write `Block -> ProvidedStorageLocation` mappings, list or read mappings, and close resources. Storage implementations obtain `BlockAliasMap.Reader` or `Writer` instances by block pool id, refresh their backing stores, and close them. NameNode audit flow initializes logger implementations during service startup, invokes audit logging from critical NameNode sections, and expects audit methods to return quickly. `INodeAttributeProvider` flow is startup `start()`, repeated attribute or access-control lookups by path/inode, then shutdown `stop()`.

## State and Persistence Behavior

The XML itself is a persisted release artifact and should remain stable except for regenerated JDiff metadata. Within the represented APIs, persistence is mainly in alias-map implementations: `LevelDBFileRegionAliasMap` persists file-region mappings in LevelDB, while `TextFileRegionAliasMap` persists them as delimited text files. `InMemoryAliasMap` presents an in-memory protocol implementation over LevelDB-oriented data and serializes/deserializes `Block` and `ProvidedStorageLocation` values using protobuf bytes. `FileRegion` equality and hashing are part of stable metadata identity for provided block regions.

Audit logging state is external to this XML but implied by `HdfsAuditLogger` extension points: implementations may use user, delegation-token, caller-context, and file-status state to format durable audit records. `INodeAttributeProvider` can introduce external metadata state or external policy engines through custom attributes and access-control enforcers.

## Dependencies and Integration Points

The generated command line records a large Hadoop 3.2.0 build classpath. The APIs themselves integrate with Hadoop `Configuration`, `Path`, `FileStatus`, `Block`, `ProvidedStorageLocation`, `InMemoryAliasMapProtocol`, `DelegationTokenSecretManager`, `CallerContext`, `UserGroupInformation`, Java `InetAddress`, `Optional`, and `IOException`, plus protobuf parse exceptions. Operational integration points are JournalNode JMX, NameNode audit logging, provided-storage alias-map bootstrapping, block alias readers/writers, and NameNode inode attribute and permission checking plugins.

## Risks and Test Signals

The primary risk for this file is accidental public API drift: any change to abstractness, parameters, return types, exceptions, or visibility can break downstream HDFS integrations even when implementation code still compiles internally. The 3.2.0 audit surface is especially sensitive because one `HdfsAuditLogger` overload is concrete while another is abstract; subclasses built against this baseline may rely on that default delegation behavior. Alias-map serialization helpers are also compatibility-sensitive because they expose raw protobuf byte conversion and concrete exception types.

Useful test signals include JDiff comparisons against adjacent releases, compilation of downstream audit logger and alias-map implementations, provided-storage tests that round-trip `Block` and `ProvidedStorageLocation` bytes, LevelDB/text alias-map read-write-refresh-close tests, JournalNode MXBean status assertions, and NameNode tests that verify audit logging remains fast inside critical sections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.0.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.1.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.1.xml

## Purpose

`Apache_Hadoop_HDFS_3.2.1.xml` is the JDiff public API baseline for `Apache Hadoop HDFS 3.2.1`, generated on 2019-09-10 by the Hadoop public-annotation JDiff doclet. It persists the HDFS API contract for release-to-release compatibility checks. The package documentation repeats the HDFS design statement: HDFS implements `org.apache.hadoop.fs.FileSystem`, follows a GFS-like distributed architecture, and permits a single writer that appends an ordered byte stream.

The file retains the same 45 package declarations, 10 public classes/interfaces, 47 public methods, and 2 public fields seen in the 3.2.0 baseline. Its substantive scope remains JournalNode management, provided-storage alias mapping, block alias metadata, NameNode audit logging, and inode attribute/access-control extension.

## Important APIs, Types, and Functions

`JournalNodeMXBean` exposes `getJournalsStatus()` as the public JMX method for JournalNode journal status.

`InMemoryAliasMap` remains the public `InMemoryAliasMapProtocol` and `Configurable` implementation. Its API includes `setConf`, `getConf`, static `init(Configuration, blockPoolID)`, `list(Optional marker)`, `read(Block)`, `write(Block, ProvidedStorageLocation)`, `getBlockPoolId`, `close`, static protobuf deserializers `fromProvidedStorageLocationBytes(byte[])` and `fromBlockBytes(byte[])`, and static serializers `toProtoBufBytes(ProvidedStorageLocation)` and `toProtoBufBytes(Block)`. Parse failures still expose `com.google.protobuf.InvalidProtocolBufferException`.

The provided-storage data model remains `BlockAlias` and `FileRegion`. `FileRegion` maps block identity to a path, offset, length, generation stamp, and optional nonce through constructors, then exports block and provided-location getters plus equality/hash semantics.

`BlockAliasMap` remains the abstract persistence abstraction for provided blocks. `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap` provide configurable concrete readers and writers. Text storage additionally exposes conversion between block pool ids and alias-map file names.

The important 3.2.1 API distinction is in `HdfsAuditLogger`: the overload `logAuditEvent(..., CallerContext, UserGroupInformation, DelegationTokenSecretManager)` is abstract in this file, whereas the 3.2.0 snapshot recorded it as concrete. The base seven-argument audit method is still concrete, and the overload without caller context but with token state is abstract. This means custom audit loggers targeting 3.2.1 must implement both extended audit methods. `AuditLogger` still defines only `initialize(Configuration)` and the seven-argument critical-section logging method. `INodeAttributeProvider` remains the NameNode plugin hook for attribute lookup and access-control enforcer replacement.

## Control Flow

The XML control flow is a JDiff declaration tree under `<api name="Apache Hadoop HDFS 3.2.1">`; compatibility tools read package and member declarations and compare them with another release's XML. The file's value is in exact public signatures and abstractness flags, not executable behavior.

The represented runtime flow follows the same HDFS extension paths as 3.2.0. JournalNode state is exported through JMX. Provided-storage bootstrap initializes alias maps by block pool, reads and writes block mappings, and closes persistent resources. Block alias maps provide reader/writer handles over LevelDB or text storage. NameNode startup initializes audit loggers and inode attribute providers; request handling invokes audit logging and attribute/access-control lookups; shutdown stops providers and closes stateful resources.

## State and Persistence Behavior

The XML is a stable generated artifact for compatibility history. The APIs it records manage state in several places: alias map contents are persisted in LevelDB or text files, `InMemoryAliasMap` converts map entries to protobuf bytes, `FileRegion` carries durable provided-storage offsets and lengths, audit logger implementations may write durable security records, and inode attribute providers may consult or cache external metadata and policy state.

The abstractness change in the caller-context audit overload affects state propagation. Because subclasses must implement the overload directly in 3.2.1, caller context and delegation-token tracking are less likely to be silently ignored by inherited default behavior, but downstream subclasses compiled against 3.2.0 may require source updates.

## Dependencies and Integration Points

This baseline integrates with Hadoop `Configuration`, HDFS protocol `Block` and `ProvidedStorageLocation`, HDFS alias-map protocols, Java `Optional`, `InetAddress`, and `IOException`, protobuf parse exceptions, SLF4J loggers, `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`. Build classpath metadata shows dependency updates from 3.2.0, but the public HDFS signatures are stable except for audit abstractness.

Integration points to watch are JournalNode JMX consumers, provided-storage import/bootstrap workflows, external block alias map implementations, NameNode audit logger subclasses, and authorization plugins implemented through `INodeAttributeProvider`.

## Risks and Test Signals

The main compatibility risk is the `HdfsAuditLogger` caller-context overload becoming abstract relative to 3.2.0. Existing subclasses that relied on a concrete inherited overload may fail to compile or instantiate. Alias-map and inode-provider APIs remain stable but still expose raw persistence and security extension points, so serialized protobuf compatibility, block pool id file naming, and permission-enforcer delegation need regression coverage.

Strong test signals include JDiff verification against 3.2.0 and 3.2.2, downstream compilation of custom `HdfsAuditLogger` subclasses, tests that caller context and token tracking are preserved in audit records, alias-map read/write/list round trips for LevelDB and text implementations, and NameNode permission tests exercising `INodeAttributeProvider`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.1.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.2.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.2.xml

## Purpose

`Apache_Hadoop_HDFS_3.2.2.xml` is the generated JDiff API snapshot for `Apache Hadoop HDFS 3.2.2`, generated on 2021-01-03. Its job is to preserve the public HDFS API surface for compatibility comparison, not to implement behavior. The root metadata records doclet invocation, classpath, source path, API name, and JDiff schema version. The HDFS package documentation continues to state the distributed `FileSystem` contract and the single-writer ordered byte-stream model.

The exported API shape is the same as 3.2.1: 45 package declarations, 10 public classes/interfaces, 47 methods, and 2 public fields. The important classes remain `JournalNodeMXBean`, `InMemoryAliasMap`, `BlockAlias`, `FileRegion`, `BlockAliasMap`, `LevelDBFileRegionAliasMap`, `TextFileRegionAliasMap`, `AuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider`.

## Important APIs, Types, and Functions

JournalNode management is represented by `JournalNodeMXBean#getJournalsStatus()`, a string-returning JMX method for journal status.

Provided-storage lookup is represented by `InMemoryAliasMap`, which is both configurable and protocol-facing. It declares lifecycle and access methods for setting configuration, initializing a map for a block pool, listing from an optional marker, reading a block mapping, writing a `Block` to `ProvidedStorageLocation` mapping, returning the block pool id, closing resources, and converting HDFS block/location objects to and from protobuf bytes.

The block alias model is split into the minimal `BlockAlias` interface and the `FileRegion` implementation, which represents a provided block as a file path region. `FileRegion` constructors cover long block id/path/offset/length/generation-stamp forms, a nonce-bearing form, and a direct `(Block, ProvidedStorageLocation)` form.

Persistent map implementations are mediated by abstract `BlockAliasMap`. It defines reader and writer creation by options and block pool id, plus `refresh()` and `close()`. `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap` implement this contract and Hadoop `Configurable`. The text implementation also keeps public helpers for block-pool-id filename conversion.

NameNode audit integration uses `AuditLogger` and `HdfsAuditLogger`. In 3.2.2, as in 3.2.1, both extended `HdfsAuditLogger` overloads that include delegation-token state are abstract; only the simpler seven-argument overload is concrete. `INodeAttributeProvider` continues to define startup/shutdown, path/inode attribute lookup by string, string array, or byte components, and optional replacement of the default access-control enforcer.

## Control Flow

JDiff processing flow reads the XML from top to bottom and treats each package and member declaration as a compatibility contract. For HDFS runtime implications, the main flows are: JournalNode exposes status via MXBean; NameNode/provided-storage code initializes alias maps; clients write, read, and list block aliases; storage implementations open readers/writers and refresh persistent state; NameNode initializes audit and inode plugins; request handling uses audit logging and attribute/access-control callbacks; shutdown closes maps and stops providers.

Audit logging is explicitly documented as critical-section work: `AuditLogger#logAuditEvent` must return quickly because NameNode invokes it during core operations. That timing contract is as important as the method signature for implementers.

## State and Persistence Behavior

The XML persists a release-level API state. In the captured APIs, state and persistence are concentrated in block alias maps. `LevelDBFileRegionAliasMap` implies durable key/value storage for file-region mappings; `TextFileRegionAliasMap` implies file-based persistence and stable filename derivation from block pool ids; `InMemoryAliasMap` exposes serialized bytes for block and location records; `FileRegion` encodes the durable tuple needed to find externally provided bytes.

Audit loggers persist operational security events outside this XML, and the API exposes enough request context to include success, user, remote address, command, source/destination, file status, caller context, current user, and delegation-token secret manager state. `INodeAttributeProvider` can layer external state over inode attributes and authorization.

## Dependencies and Integration Points

Public signatures depend on Hadoop common and HDFS classes, Java networking and optional types, Java IO exceptions, protobuf exceptions from `com.google.protobuf`, and SLF4J. The generated classpath records dependency updates relative to earlier 3.2 releases, but the API signatures remain aligned with 3.2.1.

The integration surface is broad despite the small XML: JournalNode JMX monitoring, NameNode security audit plugins, external authorization providers, provided-storage alias map readers/writers, bootstrap/import code that consumes `FileRegion`, and downstream code that implements or subclasses the abstract types.

## Risks and Test Signals

The biggest risk is treating this XML as unimportant generated noise. It is a compatibility oracle; changing it without corresponding API intent can hide a public API break. The stable 3.2.1-to-3.2.2 API suggests downstream source compatibility, so any diff beyond generation metadata and dependency classpath should be investigated. Alias-map serialization is still risky because exception types and byte formats are public. Audit logging remains performance-sensitive and security-sensitive.

Useful tests are JDiff comparisons against 3.2.1 and 3.2.3, downstream compilation of alias-map and audit extensions, protobuf round-trip tests for `Block` and `ProvidedStorageLocation`, LevelDB/text alias-map persistence tests across process restart, audit logging latency and token-tracking tests, and NameNode authorization tests using `INodeAttributeProvider`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.2.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.3.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.3.xml

## Purpose

`Apache_Hadoop_HDFS_3.2.3.xml` is the JDiff public API record for `Apache Hadoop HDFS 3.2.3`, generated on 2022-03-20. It is a compatibility artifact used to compare public HDFS APIs between release baselines. The XML keeps the same root structure as adjacent releases: JDiff schema metadata, doclet command line, HDFS package documentation, package declarations, and selected public annotated classes, interfaces, methods, constructors, fields, parameters, exceptions, and docs.

The public API inventory remains stable with 45 packages, 10 classes/interfaces, 47 methods, and 2 fields. It preserves HDFS's documented one-writer ordered-stream semantics and captures the same public extension surfaces as 3.2.2.

## Important APIs, Types, and Functions

`JournalNodeMXBean#getJournalsStatus()` is the only public JournalNode MXBean method in this snapshot.

`InMemoryAliasMap` remains the main public alias-map protocol implementation. Its methods cover configuration, static initialization by block pool, listing, reading, writing, block-pool-id access, closing, and protobuf serialization helpers for `Block` and `ProvidedStorageLocation`.

`BlockAlias` and `FileRegion` define the provided-storage data model. `FileRegion` remains the concrete representation of a block stored as a file path region with offset/length metadata, and it exposes equality and hashing for use in collections and comparisons.

`BlockAliasMap` defines the persistence abstraction and resource lifecycle. `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap` remain the public implementations, with `TextFileRegionAliasMap` carrying static filename conversion helpers.

NameNode extension APIs are unchanged from 3.2.2. `AuditLogger` has `initialize` and the base `logAuditEvent`. `HdfsAuditLogger` has one concrete base overload and two abstract extended overloads carrying caller context and/or delegation-token tracking inputs. `INodeAttributeProvider` supports start/stop, three forms of attribute lookup, and optional access-control enforcer replacement.

## Control Flow

The XML's own flow is a declarative API tree consumed by JDiff. The HDFS flows it captures are lifecycle-oriented. Alias maps are configured, initialized for a block pool, used for reads/writes/lists, refreshed through implementation-specific storage, and closed. NameNode security extensions are initialized at startup, invoked during operations, and stopped at shutdown. Audit logger calls happen in a NameNode critical path and must be implemented as low-latency logging or dispatch.

Provided-storage flow is the clearest cross-class sequence: a `FileRegion` provides block-to-location identity, `InMemoryAliasMap` exposes protocol operations over those mappings, `BlockAliasMap` provides pluggable persistence access, and LevelDB/text implementations store and retrieve the mappings.

## State and Persistence Behavior

The artifact itself persists the 3.2.3 public API state. Runtime state implied by the APIs includes Hadoop configuration, block pool ids, block-to-location mappings, LevelDB or text-backed alias maps, serialized protobuf records, logger state, caller context/token tracking settings in audit implementations, and external metadata or policy state behind inode attribute providers.

Because this snapshot is stable relative to 3.2.2, persistence format expectations should remain unchanged for consumers moving between those releases. In particular, `com.google.protobuf.InvalidProtocolBufferException` is still part of the public parse-helper signatures.

## Dependencies and Integration Points

The generated classpath shows the HDFS 3.2.3 build environment, including Hadoop common/client artifacts, Jetty, Jersey, Curator, Zookeeper, Guava, protobuf, LevelDB JNI, Jackson, and SLF4J/log4j. Public method signatures integrate directly with Hadoop configuration, HDFS protocol objects, Hadoop security objects, and Java IO/network types.

Operational integration points are JournalNode monitoring, provided-storage alias map persistence, NameNode audit logging, delegation-token tracking, caller-context propagation, and external authorization through `INodeAttributeProvider.AccessControlEnforcer`.

## Risks and Test Signals

The primary risk is regression hidden behind an unchanged API count. Compatibility should be verified structurally, not by line count alone, because abstractness flags and exception types are semantically significant. Audit logger implementers remain exposed to abstract method obligations, and alias-map consumers remain exposed to protobuf and persistence format compatibility.

Test signals should include JDiff comparison against 3.2.2 and 3.2.4, API signature checks for `HdfsAuditLogger` abstract overloads, provided-storage import/export tests, alias-map restart persistence tests for both LevelDB and text, audit logger performance/security tests, and `INodeAttributeProvider` permission-enforcer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.3.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.4.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.4.xml

## Purpose

`Apache_Hadoop_HDFS_3.2.4.xml` is the JDiff baseline for `Apache Hadoop HDFS 3.2.4`, generated on 2022-07-12. It records the public annotated HDFS API for compatibility checks. Like the other snapshots in this group, it is generated metadata rather than executable code, and its source value is the exact public package/type/member declaration set.

The file declares 45 packages, 10 public classes/interfaces, 47 methods, and 2 public fields. Its substantive API surface is the same as 3.2.3: JournalNode status, provided-storage alias map protocol and persistence, block-region metadata, NameNode audit logging, and NameNode inode attribute/access-control extension.

## Important APIs, Types, and Functions

The JournalNode management API is `JournalNodeMXBean#getJournalsStatus()`.

`InMemoryAliasMap` exposes the provided-storage map protocol, Hadoop configuration hooks, static initialization for a block pool, listing with an optional marker, block lookup and write, block-pool-id access, resource close, and protobuf conversion helpers. In 3.2.4 the parse helpers still publish `com.google.protobuf.InvalidProtocolBufferException`.

`BlockAlias` and `FileRegion` describe provided HDFS blocks. `FileRegion` constructors support block id/path/offset/length/generation-stamp combinations, an optional nonce byte array, and direct construction from `Block` plus `ProvidedStorageLocation`.

`BlockAliasMap` abstracts persistent alias-map storage through reader/writer factories, `refresh`, and `close`. `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap` implement it and expose `setConf`, `getConf`, `getReader`, `getWriter`, `refresh`, `close`, and public `LOG` fields. `TextFileRegionAliasMap` also provides `blockPoolIDFromFileName(Path)` and `fileNameFromBlockPoolID(String)`.

`AuditLogger` and `HdfsAuditLogger` define the NameNode audit extension contract. By 3.2.4 both extended `HdfsAuditLogger` overloads are abstract, including the overload with `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`. `INodeAttributeProvider` defines the NameNode attribute provider lifecycle and access-control integration.

## Control Flow

JDiff tools consume the XML as a release baseline and compare declarations across versions. The runtime control flow represented by those declarations starts with service/plugin initialization (`setConf`, `init`, `initialize`, `start`), proceeds through request-time operations (`read`, `write`, `list`, audit events, inode attribute lookups, access-control enforcement), then uses refresh and close/stop methods for persistence and lifecycle cleanup.

The alias-map flow has explicit persistence handoffs: callers use protocol-level map operations, while concrete `BlockAliasMap` implementations provide storage-specific readers and writers. The audit flow remains latency-sensitive because NameNode audit calls occur in critical sections.

## State and Persistence Behavior

The XML file is a persisted compatibility state for HDFS 3.2.4. Captured persistent runtime state includes LevelDB and text alias-map stores, serialized protobuf bytes for block/location records, block pool ids, file-region metadata, audit log outputs, and optional external inode metadata or authorization state. `refresh()` on alias maps signals that the persistent backing store may be reloaded or synchronized without replacing the API object.

Compared with 3.2.3, public signatures and abstractness remain stable. Compared with 3.2.0, the audit logger abstractness differs, so long-lived downstream subclasses should be tested against the exact minor release baseline.

## Dependencies and Integration Points

The doclet command line records an updated 3.2.4 dependency set, including newer SLF4J, HTTP components, Curator, Zookeeper, Guava, Jetty, Jackson, Netty, reload4j binding, protobuf, and LevelDB JNI. Public signatures integrate with Hadoop common/HDFS classes, protobuf exceptions, Java IO/network types, and Hadoop security/token classes.

Key integration points are JDiff release checks, JournalNode JMX dashboards, provided-storage block alias importing, LevelDB/text alias-map implementations, NameNode audit logger plugins, caller-context and token-tracking propagation, and external permission logic through `INodeAttributeProvider`.

## Risks and Test Signals

The compatibility risk is highest around extension points and public exception types. A subclass of `HdfsAuditLogger` must implement the abstract extended methods in this baseline. `InMemoryAliasMap` exposes concrete protobuf exception classes, so the protobuf package remains part of the public contract until the 3.3.x shaded-protobuf change. Alias-map persistence tests must cover both storage implementations and block-pool filename conversion.

Test signals include JDiff comparison against 3.2.3 and 3.3.1, downstream compilation of custom audit loggers and inode providers, protobuf serialization round trips, block alias map read/write/list/refresh/close tests, JournalNode MXBean checks, audit latency tests, and authorization tests that exercise replacement access-control enforcers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.2.4.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.1.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.1.xml

## Purpose

`Apache_Hadoop_HDFS_3.3.1.xml` is the JDiff public API baseline for `Apache Hadoop HDFS 3.3.1`, generated on 2021-06-15. It records the public annotated HDFS API surface for compatibility comparison against earlier and later Hadoop releases. The package documentation still describes HDFS as a distributed `FileSystem` implementation with a single writer and ordered byte-stream append semantics.

This snapshot keeps the same 45 package declarations but expands the exported API to 11 public classes/interfaces, 56 methods, and 8 fields. Relative to the 3.2.4 baseline, it adds JournalNode MXBean methods, adds alias-map bootstrap transfer helpers, changes protobuf parse exception types to Hadoop shaded protobuf, and introduces the public abstract `DefaultAuditLogger`.

## Important APIs, Types, and Functions

`JournalNodeMXBean` grows from one method to four. In addition to `getJournalsStatus()`, it exposes `getHostAndPort()`, `getClusterIds()`, and `getVersion()`. These additions make JournalNode JMX more useful in multi-cluster and version-aware monitoring deployments.

`InMemoryAliasMap` keeps its configuration, initialization, list/read/write, block-pool id, close, and byte conversion APIs, but its protobuf parse helpers now throw `org.apache.hadoop.thirdparty.protobuf.InvalidProtocolBufferException` instead of `com.google.protobuf.InvalidProtocolBufferException`. It also adds two static bootstrap helpers: `transferForBootstrap(HttpServletResponse, Configuration, InMemoryAliasMap)`, which transfers the alias map as a tar.gz archive for standby NameNode bootstrap, and `completeBootstrapTransfer(File)`, which extracts a transferred alias-map archive on the receiving side.

`BlockAlias`, `FileRegion`, `BlockAliasMap`, `LevelDBFileRegionAliasMap`, and `TextFileRegionAliasMap` keep the same core APIs as 3.2.x. They continue to model provided block locations and persistent alias map readers/writers.

NameNode audit logging changes materially. `DefaultAuditLogger` appears as a new public abstract class extending `HdfsAuditLogger`. It declares abstract `initialize(Configuration)`, `logAuditMessage(String)`, and both extended `logAuditEvent` overloads with token tracking and optional `CallerContext`. It also exposes protected state fields: `STRING_BUILDER` as a `ThreadLocal`, volatile `isCallerContextEnabled`, length limits `callerContextMaxLen` and `callerSignatureMaxLen`, `logTokenTrackingId`, and `debugCmdSet`. `HdfsAuditLogger` remains abstract, with its caller-context extended overload abstract in this baseline. `AuditLogger` and `INodeAttributeProvider` remain the core interfaces for audit and inode extension.

## Control Flow

The XML control flow is declarative JDiff structure under the 3.3.1 API root. The operational flow represented by new APIs is broader than 3.2.x. JournalNode monitoring can now query journal status, endpoint identity, cluster ids, and Hadoop version. Alias-map standby bootstrap can stream an archive through a servlet response, transfer it from active to standby NameNode, and complete extraction from a local file. Provided-storage operations still initialize maps by block pool, list/read/write entries, refresh persistent readers/writers, and close resources.

Audit flow now has an explicit base abstraction for default audit logging. Implementations initialize from configuration, build or emit audit messages through `logAuditMessage`, include caller context and token tracking depending on protected configuration state, and use thread-local string building to reduce per-call allocation. NameNode request flow still invokes audit logging in critical sections, so these methods must remain fast.

## State and Persistence Behavior

The XML persists a 3.3.1 API state and highlights a compatibility boundary with the 3.2.x line. Runtime persistence includes LevelDB/text alias-map storage, tar.gz alias-map bootstrap archives, protobuf-serialized block and provided-location bytes using Hadoop shaded protobuf classes, audit log outputs, audit logger configuration fields, and external inode metadata or authorization state.

`DefaultAuditLogger` introduces visible mutable/protected state for caller context enablement, maximum caller context/signature length, token tracking, debug command selection, and reusable string builders. This state is part of the extension surface for subclasses and should be treated as compatibility-sensitive. The shaded protobuf exception type means downstream code catching `com.google.protobuf.InvalidProtocolBufferException` must be updated for the 3.3.1 API.

## Dependencies and Integration Points

The build classpath records Hadoop 3.3.1 dependency changes, including Hadoop third-party shaded protobuf and shaded Guava, Curator 4.x, Zookeeper 3.5.x, Jetty 9.4.x, Jackson 2.10.x, Netty 4.1.x, and Hadoop common/client artifacts. Public signatures integrate with `javax.servlet.http.HttpServletResponse` for bootstrap transfer, Java `File`, Hadoop `Configuration`, HDFS alias-map and protocol classes, Hadoop shaded protobuf exceptions, Hadoop security/token classes, `CallerContext`, and Java network/IO types.

Important integration points are JournalNode JMX monitoring, active-to-standby NameNode bootstrap for provided-storage alias maps, downstream alias-map implementations, audit logger subclasses built on `DefaultAuditLogger`, token tracking and caller-context audit formatting, and inode attribute/access-control plugins.

## Risks and Test Signals

The largest risks are public API migration risks from 3.2.x. Added JournalNode MXBean methods may be source-compatible for interface consumers only if implementations supply defaults or the generated abstract flags match actual Java default methods; implementers should verify their concrete MXBean classes. Shaded protobuf exception types are a source-level break for code catching the old exception package. The new bootstrap transfer helpers introduce archive creation/extraction and servlet-response behavior, so path traversal, partial transfer, compression, and cleanup failures matter. `DefaultAuditLogger` exposes protected mutable fields, making subclass behavior and thread-safety part of the public contract.

Test signals include JDiff comparison against 3.2.4, downstream compilation of JournalNode MXBean and audit logger implementations, alias-map bootstrap transfer tests between active and standby NameNodes, archive extraction safety tests, shaded protobuf round-trip and exception-catching tests, audit formatting tests for caller context and token tracking limits, and existing LevelDB/text alias-map persistence tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.1.xml -->
