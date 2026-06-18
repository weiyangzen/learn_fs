# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/DefaultAuditLogger.java

## Purpose
`DefaultAuditLogger` is an evolving public base class for NameNode and Router audit loggers. It captures shared audit logging configuration and requires subclasses to implement initialization and event emission.

## Important APIs and Types
Fields include a thread-local `StringBuilder`, caller context enablement and max lengths, token tracking ID logging flag, and a debug command set. Abstract methods are `initialize`, `logAuditMessage`, and two overloads of `logAuditEvent`, one with `CallerContext`.

## Control Flow
This base class only manages caller context enablement through package-private setter/getter. Subclasses decide how to format and emit audit events, including user, remote address, command, source/destination, status, caller context, UGI, and delegation token secret manager.

## State and Persistence
State is process-local logger configuration. Audit event persistence depends on subclass output targets such as logs.

## Dependencies and Integration
It extends `HdfsAuditLogger` and integrates with `Configuration`, `FileStatus`, `CallerContext`, `UserGroupInformation`, and `DelegationTokenSecretManager`.

## Risks and Test Signals
Subclasses must clear/reuse the thread-local builder correctly to avoid leaking prior event text. Caller context length enforcement is not implemented here, so subclass tests must verify truncation and signature handling. Tests should cover both overloads, token tracking IDs, debug command behavior, and caller-context enable/disable transitions.
