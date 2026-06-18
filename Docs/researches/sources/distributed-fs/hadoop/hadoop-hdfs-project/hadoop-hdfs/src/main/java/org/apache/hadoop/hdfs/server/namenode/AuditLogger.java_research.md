# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/AuditLogger.java

Purpose: public evolving interface for pluggable NameNode audit logging.

Important APIs/types/functions: `initialize(Configuration conf)` configures the logger. `logAuditEvent(boolean succeeded, String userName, InetAddress addr, String cmd, String src, String dst, FileStatus stat)` records an audit event including authorization result, user, remote address, command, source/destination paths, and optional file status.

Control flow: NameNode audit paths call `logAuditEvent()` during request handling, including critical sections, so implementations must return quickly.

State and persistence behavior: interface has no state; implementations may write logs, metrics, or external events. The contract explicitly encourages low-latency behavior to avoid NameNode stalls.

Dependencies and integration points: public API annotated `InterfaceAudience.Public` and `InterfaceStability.Evolving`; used by NameNode audit logging configuration and custom audit logger plugins.

Risks: slow or blocking implementations can harm NameNode throughput. The evolving annotation permits API changes across versions. Implementations need to handle null `dst`/`stat` values depending on command.

Test signals: audit logging tests in the broader NameNode suite usually validate default and configured audit logger behavior; this interface itself is compile-time contract.
