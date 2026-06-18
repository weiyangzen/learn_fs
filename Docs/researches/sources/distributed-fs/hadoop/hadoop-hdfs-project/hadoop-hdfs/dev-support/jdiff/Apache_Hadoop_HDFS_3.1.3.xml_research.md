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
