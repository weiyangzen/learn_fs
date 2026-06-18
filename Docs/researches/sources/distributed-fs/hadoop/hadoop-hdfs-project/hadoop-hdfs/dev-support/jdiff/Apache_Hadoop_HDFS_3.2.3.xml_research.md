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
