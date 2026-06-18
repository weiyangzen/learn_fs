# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.5.xml

## Purpose

`Apache_Hadoop_HDFS_3.3.5.xml` is the generated JDiff API description for `Apache Hadoop HDFS 3.3.5`, generated on Tue Mar 14 18:28:07 UTC 2023. The file was read as a complete 835-line XML source. It preserves the same public API subtree as the 3.3.2, 3.3.3, and 3.3.4 files; release-specific differences are confined to generated metadata and dependency classpath content.

## Important APIs, Types, and Functions

The snapshot continues to expose the same HDFS public APIs: the package-level HDFS single-writer append contract; JournalNode JMX management via `JournalNodeMXBean`; LevelDB-backed alias map operations in `InMemoryAliasMap`; provided-block modeling through `BlockAlias` and `FileRegion`; block alias map abstraction and its LevelDB/text implementations; NameNode and Router audit logging contracts; and the inode attribute/access-control extension point.

## Control Flow

No runtime code executes from this XML. In the represented HDFS flow, JMX clients query JournalNode status; provided-storage bootstrap and block lookup code drives alias-map readers/writers and archive transfer; audit loggers are initialized and invoked during filesystem requests; and custom inode attribute providers participate in NameNode lifecycle and access-control decisions.

## State and Persistence Behavior

The XML persists a generated API snapshot. The captured APIs interact with durable HDFS-adjacent state: alias-map databases or files, bootstrap archives, protobuf-serialized mappings, audit logs, and external authorization metadata. `DefaultAuditLogger` state is process-local configuration, while alias-map state is explicitly persistent and block-pool scoped.

## Dependencies and Integration Points

The 3.3.5 command-line comment shows a larger dependency refresh without public API movement. Notable classpath signals include commons-net 3.9.0, Jetty 9.4.48, Jersey 1.19.4 plus `com.github.pjfanning:jersey-json` 1.20, Jettison 1.5.3, commons-configuration2 2.8.0, commons-text 1.10.0, Gson 2.9.0, Woodstox 5.4.0, `org.openlabtesting:leveldbjni-all` 1.8, Jackson databind 2.12.7.1, and a Java 8 arm64 build path. API-signature integration remains Hadoop configuration/protocol/security classes, servlet response handling, protobuf, Java file/network types, and SLF4J logging.

## Risks and Edge Cases

The public API stayed stable while implementation dependencies changed, so raw XML diffs can obscure the real conclusion. Dependency upgrades can still affect runtime behavior behind the stable signatures, especially HTTP transfer, JSON/JAX-RS support, LevelDB JNI packaging, and logging. Alias-map compatibility across LevelDB JNI providers, bootstrap archive extraction safety, and audit logger latency remain the main operational risks.

## Test Signals

Tests should include semantic JDiff comparison against 3.3.4 and 3.3.2, plus runtime compatibility checks around alias-map persistence using the refreshed LevelDB JNI path, bootstrap transfer over servlet response, JournalNode MXBean status, audit logger behavior under token/caller-context configurations, and NameNode authorization with external inode attributes. A non-empty, schema-valid XML artifact with the same package/type/member subtree is the release-documentation signal.
