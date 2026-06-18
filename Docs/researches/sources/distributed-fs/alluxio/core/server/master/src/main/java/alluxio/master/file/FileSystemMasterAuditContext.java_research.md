# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/FileSystemMasterAuditContext.java

## Purpose
`FileSystemMasterAuditContext` captures one file-system master operation for asynchronous user access audit logging. It accumulates authorization, success, identity, command, path, inode permission, timing, client-version, and protocol fields, then appends itself to an `AsyncUserAccessAuditLogWriter` when closed.

## Important APIs, types, and functions
The class implements `AuditContext`. Fluent setters include `setAllowed`, `setSucceeded`, `setCommand`, `setSrcPath`, `setDstPath`, `setUgi`, `setAuthType`, `setIp`, `setSrcInode`, `setCreationTimeNs`, and `setClientVersion`. `close()` computes elapsed time and submits the context to the async writer. `toString()` formats the audit line, including inode owner/group/mode when a source inode is available.

## Control flow
Callers create the context around an RPC, populate fields as permission checks and operations proceed, and close it after the operation. Closing is no-op when no writer is configured. Formatting branches on whether `mSrcInode` is present and on `USER_CLIENT_REPORT_VERSION_ENABLED` for including client version.

## State and persistence behavior
The context is not thread-safe and is intended for one operation. It does not persist metadata itself, but it emits audit records to the configured async log writer. The elapsed time is derived from `System.nanoTime()` minus the stored creation time.

## Dependencies and integration points
It depends on master audit interfaces, authentication type, inode metadata, permission mode extraction, `AlluxioURI`, and global configuration. It is integrated with `DefaultFileSystemMaster` audit-context creation and with `InodeSyncStream` when metadata loading wants the audit source inode populated after locking.

## Risks
Forgetting to set creation time yields misleading execution-time values. Missing source inode produces `perm=null`, which is expected for some paths but loses useful audit context. Because `toString()` pulls from mutable fields, reusing one instance across operations would corrupt logs. Client-version emission depends on global config at formatting time.

## Test signals
Audit-log tests should assert line formatting with and without source inode, success/allowed flags, optional client-version field, and close behavior when the writer is null. Integration signals come from RPC audit tests that validate operation-specific command and path fields.
