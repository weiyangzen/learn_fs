# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateFileContext.java

Purpose: wraps `CreateFilePOptions` for file creation in the master, adding master-only runtime state that is not represented directly in the protobuf. It extends `CreatePathContext`, so it inherits owner/group, ACL, TTL, write type, metadata-load, fingerprint, xattr, mount-point, and operation-time behavior.

Important APIs and types: static factories `create`, `mergeFrom`, `mergeFromDefault`, and `defaults` construct contexts from raw, default-merged, or already-defaulted file options. The nested `CompleteFileInfo` carries container id, final length, and block ids for metadata sync paths that create an already-complete file. `setCacheable`, `isCacheable`, `setCompleteFileInfo`, and `getCompleteFileInfo` expose the extra state.

Control flow: normal RPC paths call `mergeFrom` to merge user options over `FileSystemOptionsUtils.createFileDefaults`; metadata sync can use `mergeFromDefault` with a known defaults object and then mutate fields such as block size, write type, fingerprint, owner, group, and xattrs. `getOperationId` reads the common options operation id before falling back to the base context.

State and persistence behavior: the class itself is transient and not journaled, but its values drive journaled inode creation through file-master internals. `CompleteFileInfo` is a critical persistence signal because it lets metadata sync create completed file metadata with specific container and block identity rather than an open file placeholder.

Dependencies and integration points: depends on gRPC option builders, global configuration defaults, `FileSystemOptionsUtils`, `OperationId`, and the `CreatePathContext` extraction logic. It is consumed by `DefaultFileSystemMaster` creation paths and by `DefaultSyncProcess.createInodeFileMetadata`.

Risks: mutable protobuf builders and mutable context fields are not thread-safe. `mCompleteFileInfo` is nullable but returned without `Optional`, so callers must handle absence. `mergeFromDefault` assumes its input already represents the desired defaults and intentionally skips the normal master-default merge.

Test signals: useful tests should cover default merging, operation-id propagation, cacheable and complete-file metadata sync creation, and behavior when no complete info is supplied. Existing broader metadata-sync and create-file tests are the likely behavioral signal rather than this wrapper having isolated tests.
