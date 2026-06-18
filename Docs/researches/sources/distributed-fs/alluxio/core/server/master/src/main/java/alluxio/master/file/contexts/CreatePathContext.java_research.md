# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreatePathContext.java

Purpose: provides the shared master-side context for creating files and directories. It wraps either `CreateFilePOptions.Builder` or `CreateDirectoryPOptions.Builder` and carries derived fields plus internal-only state needed by `InodeTree.createPath` and file master create operations.

Important APIs and types: generic type parameters bind the protobuf builder type and fluent subtype. Getters extract mode, recursive flag, TTL, TTL action, persisted state, write type, xattrs, xattr propagation, owner, group, ACL, fingerprints, mount-point flag, operation time, metadata-load flag, and parent-directory persistence policy. Setters mutate runtime context state while extracted fields are reloaded from the protobuf builder to keep consistency.

Control flow: the constructor initializes owner/group from authenticated gRPC client configuration when authentication is enabled, converts protobuf write type to `WriteType`, and converts xattr byte strings. `loadExtractedFields` branches on file versus directory builders to pull mode, recursive, TTL, and TTL action from the current builder. `setMetadataLoad` enforces that parent directory persistence may only be disabled during metadata load.

State and persistence behavior: the context is transient, but it determines journaled inode attributes. The operation timestamp becomes inode creation or modification time; `mFingerprint` and `mMissingDirFingerprint` carry UFS fingerprints; write type controls persisted state; and xattrs flow into inode metadata. The missing-directory fingerprint supplier allows lazily computing parent fingerprints during recursive metadata-load creation.

Dependencies and integration points: integrates protobuf create options, `WriteType`, `Mode`, `TtlAction`, `XAttrPropagationStrategy`, authentication/security utilities, and Alluxio constants. `CreateFileContext` and `CreateDirectoryContext` subclass it, and metadata sync relies on its metadata-load, write-through, fingerprint, and xattr hooks.

Risks: fields are mutable and the class is explicitly built on mutable protobuf builders, so sharing across threads would be unsafe. Derived fields are reloaded from protobuf on access, but write type and xattrs are separately mutable context fields, so callers must keep builder and context choices coherent. Incorrect metadata-load flags can cause undesired UFS parent creation or stale fingerprint state.

Test signals: tests should exercise file and directory builders, default owner/group initialization, metadata-load invariant enforcement, TTL/mode extraction after builder mutation, xattr propagation, and parent persistence behavior during metadata sync.
