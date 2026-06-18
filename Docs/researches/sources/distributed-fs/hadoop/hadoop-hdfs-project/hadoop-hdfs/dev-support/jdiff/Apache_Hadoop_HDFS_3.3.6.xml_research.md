# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.6.xml

## Purpose

`Apache_Hadoop_HDFS_3.3.6.xml` is the generated JDiff public API snapshot for `Apache Hadoop HDFS 3.3.6`, generated on Mon Jun 19 00:19:49 UTC 2023. The file was read as a complete 835-line XML source. It is the newest snapshot in this work item and keeps the same public package/type/member body as every listed 3.3.2 through 3.3.5 file.

## Important APIs, Types, and Functions

The API body continues to document HDFS package semantics and the stable public surface around JournalNode management, provided-storage alias maps, audit logging, and external inode attribute policy. The notable public types are `JournalNodeMXBean`, `InMemoryAliasMap`, `BlockAlias`, `FileRegion`, `BlockAliasMap`, `LevelDBFileRegionAliasMap`, `TextFileRegionAliasMap`, `AuditLogger`, `DefaultAuditLogger`, `HdfsAuditLogger`, and `INodeAttributeProvider`. No public members are added or removed relative to the earlier snapshots.

## Control Flow

The generated artifact is consumed by compatibility tooling. It describes HDFS flows in which JournalNode exposes management state, provided-storage code maps HDFS blocks to external file regions through alias-map readers/writers, bootstrap code copies alias-map state between NameNodes, audit loggers run during NameNode/Router operations, and attribute providers influence metadata and permission evaluation over the NameNode lifecycle.

## State and Persistence Behavior

The XML is static release metadata. The represented APIs can expose or mutate persistent state in JournalNode journals, LevelDB or text alias-map stores, tar.gz bootstrap archives, protobuf mapping bytes, audit logs, and external authorization systems. The API snapshot itself does not define locking, failure atomicity, or format migration rules, so those concerns must be tracked in the implementation and tests.

## Dependencies and Integration Points

The 3.3.6 classpath keeps the same public signatures while refreshing several runtime dependencies. Notable signals include ZooKeeper 3.6.3, Curator 5.2.0, Jetty 9.4.51, Jettison 1.5.4, Dropwizard metrics-core 3.2.4, Netty 4.1.89 with expanded modules, the `org.openlabtesting` LevelDB JNI artifact, Jackson 2.12.7.1, and Java 8 arm64. The doclet integration remains Hadoop annotations plus JDiff over HDFS source, with public signatures depending on Hadoop configuration, HDFS protocol classes, servlet response APIs, protobuf exceptions, security token classes, and SLF4J.

## Risks and Edge Cases

The stable API body is a positive compatibility signal, but dependency changes in the generated classpath may affect behavior outside the XML surface. Raw textual diffs should not be treated as API changes. Runtime risk remains concentrated in persistent alias-map formats, bootstrap archive transfer/extraction, JournalNode management visibility, fast audit logging in critical sections, and custom authorization providers that can override default permission behavior.

## Test Signals

A semantic comparison against all earlier listed snapshots should show no package, class, interface, method, constructor, or field changes. Additional signals are successful JDiff generation, XML schema validity, JournalNode MXBean integration tests, alias-map LevelDB/text persistence and refresh tests, protobuf conversion round trips, bootstrap archive tests, audit logger overload tests, and NameNode permission tests covering `INodeAttributeProvider` and external access-control enforcer integration.
