## sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/BulkDeleteSource.java

Purpose: optional filesystem extension for creating path-scoped `BulkDelete` operations.

Important APIs and types: single `createBulkDelete(Path)` method, throwing unsupported, illegal argument, or IO exceptions depending on support and path resolution.

Control flow: interface only. Implementations typically resolve the path and return a delete object without performing network deletion at creation time.

State and persistence behavior: none in the interface. Returned `BulkDelete` instances own any operation state.

Dependencies and integration points: paired with `BulkDelete` and `CommonPathCapabilities.BULK_DELETE`.

Risks: implementing this interface is not sufficient by itself; callers are expected to rely on successful object creation and capability probing. Path validation and symlink resolution are implementation-dependent.

Test signals: verify capability advertisement, unsupported paths, invalid paths, symlink/path resolution, and that creation itself avoids delete side effects.
