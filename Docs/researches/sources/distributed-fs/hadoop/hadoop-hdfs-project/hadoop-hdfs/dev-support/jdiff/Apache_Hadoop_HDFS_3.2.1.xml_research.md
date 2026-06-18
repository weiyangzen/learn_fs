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
