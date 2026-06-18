# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/dev-support/jdiff/Apache_Hadoop_HDFS_3.3.1.xml

## Purpose

`Apache_Hadoop_HDFS_3.3.1.xml` is the JDiff public API baseline for `Apache Hadoop HDFS 3.3.1`, generated on 2021-06-15. It records the public annotated HDFS API surface for compatibility comparison against earlier and later Hadoop releases. The package documentation still describes HDFS as a distributed `FileSystem` implementation with a single writer and ordered byte-stream append semantics.

This snapshot keeps the same 45 package declarations but expands the exported API to 11 public classes/interfaces, 56 methods, and 8 fields. Relative to the 3.2.4 baseline, it adds JournalNode MXBean methods, adds alias-map bootstrap transfer helpers, changes protobuf parse exception types to Hadoop shaded protobuf, and introduces the public abstract `DefaultAuditLogger`.

## Important APIs, Types, and Functions

`JournalNodeMXBean` grows from one method to four. In addition to `getJournalsStatus()`, it exposes `getHostAndPort()`, `getClusterIds()`, and `getVersion()`. These additions make JournalNode JMX more useful in multi-cluster and version-aware monitoring deployments.

`InMemoryAliasMap` keeps its configuration, initialization, list/read/write, block-pool id, close, and byte conversion APIs, but its protobuf parse helpers now throw `org.apache.hadoop.thirdparty.protobuf.InvalidProtocolBufferException` instead of `com.google.protobuf.InvalidProtocolBufferException`. It also adds two static bootstrap helpers: `transferForBootstrap(HttpServletResponse, Configuration, InMemoryAliasMap)`, which transfers the alias map as a tar.gz archive for standby NameNode bootstrap, and `completeBootstrapTransfer(File)`, which extracts a transferred alias-map archive on the receiving side.

`BlockAlias`, `FileRegion`, `BlockAliasMap`, `LevelDBFileRegionAliasMap`, and `TextFileRegionAliasMap` keep the same core APIs as 3.2.x. They continue to model provided block locations and persistent alias map readers/writers.

NameNode audit logging changes materially. `DefaultAuditLogger` appears as a new public abstract class extending `HdfsAuditLogger`. It declares abstract `initialize(Configuration)`, `logAuditMessage(String)`, and both extended `logAuditEvent` overloads with token tracking and optional `CallerContext`. It also exposes protected state fields: `STRING_BUILDER` as a `ThreadLocal`, volatile `isCallerContextEnabled`, length limits `callerContextMaxLen` and `callerSignatureMaxLen`, `logTokenTrackingId`, and `debugCmdSet`. `HdfsAuditLogger` remains abstract, with its caller-context extended overload abstract in this baseline. `AuditLogger` and `INodeAttributeProvider` remain the core interfaces for audit and inode extension.

## Control Flow

The XML control flow is declarative JDiff structure under the 3.3.1 API root. The operational flow represented by new APIs is broader than 3.2.x. JournalNode monitoring can now query journal status, endpoint identity, cluster ids, and Hadoop version. Alias-map standby bootstrap can stream an archive through a servlet response, transfer it from active to standby NameNode, and complete extraction from a local file. Provided-storage operations still initialize maps by block pool, list/read/write entries, refresh persistent readers/writers, and close resources.

Audit flow now has an explicit base abstraction for default audit logging. Implementations initialize from configuration, build or emit audit messages through `logAuditMessage`, include caller context and token tracking depending on protected configuration state, and use thread-local string building to reduce per-call allocation. NameNode request flow still invokes audit logging in critical sections, so these methods must remain fast.

## State and Persistence Behavior

The XML persists a 3.3.1 API state and highlights a compatibility boundary with the 3.2.x line. Runtime persistence includes LevelDB/text alias-map storage, tar.gz alias-map bootstrap archives, protobuf-serialized block and provided-location bytes using Hadoop shaded protobuf classes, audit log outputs, audit logger configuration fields, and external inode metadata or authorization state.

`DefaultAuditLogger` introduces visible mutable/protected state for caller context enablement, maximum caller context/signature length, token tracking, debug command selection, and reusable string builders. This state is part of the extension surface for subclasses and should be treated as compatibility-sensitive. The shaded protobuf exception type means downstream code catching `com.google.protobuf.InvalidProtocolBufferException` must be updated for the 3.3.1 API.

## Dependencies and Integration Points

The build classpath records Hadoop 3.3.1 dependency changes, including Hadoop third-party shaded protobuf and shaded Guava, Curator 4.x, Zookeeper 3.5.x, Jetty 9.4.x, Jackson 2.10.x, Netty 4.1.x, and Hadoop common/client artifacts. Public signatures integrate with `javax.servlet.http.HttpServletResponse` for bootstrap transfer, Java `File`, Hadoop `Configuration`, HDFS alias-map and protocol classes, Hadoop shaded protobuf exceptions, Hadoop security/token classes, `CallerContext`, and Java network/IO types.

Important integration points are JournalNode JMX monitoring, active-to-standby NameNode bootstrap for provided-storage alias maps, downstream alias-map implementations, audit logger subclasses built on `DefaultAuditLogger`, token tracking and caller-context audit formatting, and inode attribute/access-control plugins.

## Risks and Test Signals

The largest risks are public API migration risks from 3.2.x. Added JournalNode MXBean methods may be source-compatible for interface consumers only if implementations supply defaults or the generated abstract flags match actual Java default methods; implementers should verify their concrete MXBean classes. Shaded protobuf exception types are a source-level break for code catching the old exception package. The new bootstrap transfer helpers introduce archive creation/extraction and servlet-response behavior, so path traversal, partial transfer, compression, and cleanup failures matter. `DefaultAuditLogger` exposes protected mutable fields, making subclass behavior and thread-safety part of the public contract.

Test signals include JDiff comparison against 3.2.4, downstream compilation of JournalNode MXBean and audit logger implementations, alias-map bootstrap transfer tests between active and standby NameNodes, archive extraction safety tests, shaded protobuf round-trip and exception-catching tests, audit formatting tests for caller context and token tracking limits, and existing LevelDB/text alias-map persistence tests.
