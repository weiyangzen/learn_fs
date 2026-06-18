# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/DeleteContext.java

Purpose: wraps `DeletePOptions` for file-master delete operations and adds internal metadata-sync flags. It standardizes construction of delete contexts from raw builders, default master options, or default settings.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct instances. `setMetadataLoad` marks deletes caused by metadata load or sync. `skipNotPersisted` and `isSkipNotPersisted` control whether non-completed or non-persisted files are ignored during recursive sync deletes. `getOperationId` extracts common-option operation ids.

Control flow: `mergeFrom` obtains master delete defaults from `FileSystemOptionsUtils.deleteDefaults(Configuration.global(), false)` and merges user options over them. Metadata sync builds recursive, alluxio-only, unchecked delete options, then sets metadata-load and optional skip-not-persisted behavior before calling `DefaultFileSystemMaster.deleteInternal`.

State and persistence behavior: this class is not persisted itself, but it directly governs whether inode deletion journals are emitted and whether UFS deletion is bypassed. The metadata-load flag lets downstream code distinguish authoritative UFS-driven metadata reconciliation from user deletes.

Dependencies and integration points: depends on `DeletePOptions`, configuration defaults, and `OperationId`. It integrates with `DefaultSyncProcess.deletePath` and standard file-system master delete RPC handling.

Risks: `skipNotPersisted` is a subtle data-preservation flag; using it outside metadata sync could leave unexpected inode state. Because options and flags are mutable, callers should not reuse a context across independent delete requests.

Test signals: high-value tests include recursive metadata-sync deletes, skipped non-persisted files, alluxio-only behavior, operation-id propagation, and default merge behavior.
