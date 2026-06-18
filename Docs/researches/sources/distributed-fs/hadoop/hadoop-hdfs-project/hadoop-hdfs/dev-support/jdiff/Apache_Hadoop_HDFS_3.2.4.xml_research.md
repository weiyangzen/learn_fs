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
