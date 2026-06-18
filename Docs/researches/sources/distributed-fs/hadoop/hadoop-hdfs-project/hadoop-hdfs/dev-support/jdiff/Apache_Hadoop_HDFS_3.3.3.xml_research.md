# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.3.xml

## Purpose

`Apache_Hadoop_HDFS_3.3.3.xml` is the generated JDiff API description for `Apache Hadoop HDFS 3.3.3`. It was generated on Mon May 09 18:03:54 GMT 2022 using the Hadoop public-annotation JDiff doclet and the HDFS source path. The file was read as a complete 835-line XML source. Apart from the generated header, API name, and command-line classpath, the semantic API body is byte-for-byte identical to the 3.3.2 snapshot and remains identical through 3.3.6.

## Important APIs, Types, and Functions

The captured API surface is the same stable HDFS public subset as 3.3.2. It includes the HDFS package documentation for the single-writer append stream contract, `JournalNodeMXBean` for JournalNode JMX status, `InMemoryAliasMap` for LevelDB-backed block-to-provided-storage mappings, `BlockAlias` and `FileRegion` for provided block region modeling, abstract `BlockAliasMap` plus LevelDB and text implementations, NameNode/Router audit logging via `AuditLogger`, `HdfsAuditLogger`, and `DefaultAuditLogger`, and the `INodeAttributeProvider` extension point for external inode attributes and access-control enforcement.

## Control Flow

This XML has no executable flow. It documents public call paths used by HDFS: JournalNode state is exposed through MXBean getters; provided-storage alias maps are configured, opened by block pool id, read or written, refreshed, and closed; bootstrap flow streams an alias-map archive from the active side and completes extraction on a standby; audit logging is invoked synchronously during NameNode or Router operations; and `INodeAttributeProvider` is started at NameNode startup, consulted during metadata and permission checks, then stopped at shutdown.

## State and Persistence Behavior

The file is a generated compatibility artifact. The described APIs touch persistent or externally visible state through JournalNode journal metadata, LevelDB/text alias-map stores, protobuf-serialized block and provided-storage records, bootstrap archive files, audit logs, and optional external authorization metadata. The XML does not describe implementation internals, locking, or durability guarantees beyond method signatures and embedded Javadocs.

## Dependencies and Integration Points

The 3.3.3 generation classpath moved Hadoop module artifacts to 3.3.3 and updated several libraries without changing the public HDFS XML body. Notable classpath signals include SLF4J 1.7.36, Jackson 2.13.2/2.13.2.2, commons-codec 1.15, reload4j 1.2.18.3, and the same broad integration set of Hadoop common/auth/client jars, protobuf, servlet, Jetty/Jersey, ZooKeeper, Curator, Netty, and LevelDB JNI. Public signature dependencies remain Hadoop configuration, HDFS protocol objects, servlet response handling, protobuf exceptions, and security/audit classes.

## Risks and Edge Cases

The main research risk is mistaking dependency churn in the generated command-line comment for API churn. Because lines 16 onward match 3.3.2, downstream compatibility consumers should treat this as a stable API snapshot. Operational risks remain in the documented API contracts: audit loggers must not block NameNode critical sections, alias-map stores must preserve block pool isolation and on-disk format compatibility, and external attribute providers can change effective authorization.

## Test Signals

A strong test signal is a semantic XML diff against 3.3.2 showing no package/type/member changes. Other signals mirror the runtime contracts: JMX tests for JournalNode status getters, alias-map LevelDB/text round trips and bootstrap transfer, protobuf conversion tests for `Block` and `ProvidedStorageLocation`, audit logging tests for all overloads and token/caller-context options, and NameNode permission tests with custom `INodeAttributeProvider` behavior.
