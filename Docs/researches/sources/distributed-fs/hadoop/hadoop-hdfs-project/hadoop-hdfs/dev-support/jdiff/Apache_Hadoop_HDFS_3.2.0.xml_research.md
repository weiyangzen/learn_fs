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
