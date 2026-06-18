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
