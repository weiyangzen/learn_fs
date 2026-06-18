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
