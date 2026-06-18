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
