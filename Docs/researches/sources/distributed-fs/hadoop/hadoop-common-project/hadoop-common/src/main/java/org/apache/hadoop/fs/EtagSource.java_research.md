## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/EtagSource.java

Purpose: `EtagSource` is an optional interface for `FileStatus` subclasses that can expose an object or file etag. It lets clients retrieve identity/version markers when a filesystem supports them.

Important APIs and types: the single API is `String getEtag()`. The contract allows null or empty string to mean no etag.

Control flow, state, and persistence: the interface has no implementation state. Persistence and etag stability are delegated to concrete `FileStatus` and filesystem implementations.

Dependencies and integration: the interface is paired with `CommonPathCapabilities.ETAGS_AVAILABLE` and `ETAGS_PRESERVED_IN_RENAME`. Filesystem listing and status calls can return `FileStatus` instances implementing this interface so applications can perform optimistic consistency checks, cache validation, or rename-preservation checks.

Risks and test signals: risks come from inconsistent capability advertisement, empty-vs-null handling, and rename semantics. Tests should verify that status objects implement `EtagSource` only when meaningful, that capability probes match returned statuses, and that providers claiming rename preservation actually preserve etags across rename operations.
