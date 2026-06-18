# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/HdfsAuditLogger.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/HdfsAuditLogger.java

Purpose: `HdfsAuditLogger` is the evolving public HDFS audit logger extension interface. It preserves the base `AuditLogger` contract while adding HDFS-specific context needed for caller-context and delegation-token tracking.

Important APIs and types: it implements `AuditLogger`. The base seven-argument `logAuditEvent` is implemented to delegate to the richer overload with null `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`. Subclasses must implement the overload with caller context and token tracking objects, and another overload without caller context but with UGI and delegation token manager.

Control flow: default control flow is a compatibility shim: older callers invoke the base method, and the class forwards to the richer signature so subclasses can centralize formatting and token tracking. Actual logging behavior is supplied by concrete subclasses such as the default NameNode audit logger.

State and persistence behavior: this abstract class stores no state and writes nothing itself. Implementations generally persist audit records to logs and may include token tracking IDs when UGI and secret manager are available.

Dependencies and integration points: it integrates with `AuditLogger`, `FileStatus`, `CallerContext`, `UserGroupInformation`, `DelegationTokenSecretManager`, and NameNode audit call sites for commands, source/destination paths, remote addresses, and operation success.

Risks: implementers must keep both abstract overloads consistent or audit output can differ depending on call path. Null caller context, UGI, or token manager values are expected and must be handled. Because the interface is public/evolving, signature changes carry downstream compatibility risk.

Test signals: tests should verify delegation from the base method, concrete logger handling of null optional context, token tracking output when UGI/secret manager are present, and consistent formatting across overloads.
