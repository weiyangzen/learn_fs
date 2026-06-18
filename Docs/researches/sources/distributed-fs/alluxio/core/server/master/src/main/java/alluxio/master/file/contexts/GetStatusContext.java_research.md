# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/GetStatusContext.java

Purpose: wraps `GetStatusPOptions` for retrieving file or directory status from the master. It gives get-status calls the same option-merging and cancellation-tracking pattern as other file RPC contexts.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct the wrapper. `mergeFrom` uses `FileSystemOptionsUtils.getStatusDefaults(Configuration.global())`. `toString` includes the built options for debugging.

Control flow: callers merge request options over master defaults and pass the context through status resolution. Unlike create/delete/rename, it does not override `getOperationId`, so operation ids are not extracted here unless the base class changes.

State and persistence behavior: no direct persistence. Options may influence whether status retrieval triggers metadata loading or sync, but persisted inode and UFS state are handled downstream.

Dependencies and integration points: depends on `GetStatusPOptions`, configuration, option defaults, and base `OperationContext`. It integrates with the master get-status RPC and internal status paths.

Risks: thin wrappers can hide option semantics in downstream code; future status fields that need derived context state would require explicit additions. The mutable options builder must not be reused unsafely.

Test signals: default merging, status with metadata-sync common options, cancellation tracking, and debug rendering are the relevant signals.
