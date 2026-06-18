# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.4.xml

## Purpose

`Apache_Hadoop_HDFS_3.3.4.xml` is the JDiff public API snapshot for `Apache Hadoop HDFS 3.3.4`, generated on Fri Jul 29 14:04:11 GMT 2022. It is a dev-support compatibility input rather than application code. The file was read as a complete 835-line XML source, and its package/type/member subtree is identical to the 3.3.2 and 3.3.3 snapshots.

## Important APIs, Types, and Functions

The source records the same public HDFS contracts: HDFS package documentation; `JournalNodeMXBean` JMX getters for journal status, host/port, cluster ids, and version; `InMemoryAliasMap` for LevelDB-backed provided-storage alias mappings and bootstrap archive transfer; `BlockAlias` and `FileRegion` for mapping HDFS blocks to provided file regions; abstract `BlockAliasMap` readers/writers plus `LevelDBFileRegionAliasMap` and `TextFileRegionAliasMap`; audit logging interfaces and base classes; and `INodeAttributeProvider` for external attributes and access-control enforcement.

## Control Flow

The XML is parsed by tooling, not executed. It implies HDFS control flow around management, provided storage, auditing, and authorization: management clients read JournalNode state through JMX; alias-map callers obtain configured readers or writers by block pool id and operate against LevelDB or text storage; standby bootstrap copies and extracts alias-map state; audit loggers run inside NameNode/Router operation flow; and attribute providers wrap NameNode lifecycle and permission checks.

## State and Persistence Behavior

Generated metadata is static. The APIs it describes expose mutable cluster state and persistent artifacts: JournalNode journal formatting/status, provided-storage block maps in LevelDB or text files, tar.gz alias-map bootstrap archives, serialized protobuf records, audit streams, and external policy state behind `INodeAttributeProvider`. The public API does not encode transactional details, so persistence semantics must be verified in the implementation and tests.

## Dependencies and Integration Points

The 3.3.4 classpath shows dependency movement while the API body stays stable. Notable changes include OkHttp moving to the `okhttp3` 4.9.3 artifact with Okio 2.8.0 and Kotlin stdlib, Jackson 2.12.7, reload4j 1.2.22, Netty 4.1.77 with expanded Netty modules, and Xerces 2.12.2. The generated doclet still integrates Hadoop annotations, JDiff, HDFS target classes, hadoop-common/auth/client, servlet/JAX-RS/Jetty/Jersey, ZooKeeper/Curator, protobuf, SLF4J, and LevelDB JNI.

## Risks and Edge Cases

Tooling that compares raw XML will report a large single-line classpath diff even though the public API surface is unchanged. The member list also uses erased/raw type names for some generic returns such as `Optional` and `List`, so reviewers should inspect source Javadocs or Java signatures when generic compatibility matters. Runtime risk areas remain alias-map storage format compatibility, bootstrap archive handling, fast audit logging, and external authorization provider correctness.

## Test Signals

The clearest research signal is that a tail comparison after the generated header matches previous releases. CI should validate schema conformance and semantic API diffs, then rely on implementation tests for LevelDB and text alias maps, bootstrap transfer/extraction, JournalNode MXBean registration and values, audit logging with caller context and delegation token tracking, and NameNode authorization paths using custom inode attributes.
