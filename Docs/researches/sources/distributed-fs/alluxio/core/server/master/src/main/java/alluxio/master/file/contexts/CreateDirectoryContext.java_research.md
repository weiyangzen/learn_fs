# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CreateDirectoryContext.java

## Purpose
`CreateDirectoryContext` wraps `CreateDirectoryPOptions` and extends create-path context state for directory creation, including UFS status and default ACLs used when loading directory metadata from UFS.

## Important APIs, types, and functions
It extends `CreatePathContext<CreateDirectoryPOptions.Builder, CreateDirectoryContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. Extra methods include `getUfsStatus`, `setUfsStatus`, `setDefaultAcl`, `getDefaultAcl`, and an override of `getOperationId` that checks common proto options first. `toString()` includes path context and UFS status.

## Control flow
`mergeFrom` overlays caller options on `FileSystemOptionsUtils.createDirectoryDefaults(Configuration.global(), false)`. Metadata load code populates owner, group, xattrs, mode, mount-point flag, write type, ACL, default ACL, and UFS status before calling create-directory internals.

## State and persistence behavior
The context controls persisted directory metadata: mode, owner/group, ACL/default ACL, xattrs, TTL/common options, mount-point flag, write type, and operation time inherited from create-path context. The context itself is in-memory and per operation.

## Dependencies and integration points
It depends on create-directory protos, configuration defaults, `CreatePathContext`, ACL entries, `UfsStatus`, and `OperationId`. It is used by client create-directory RPCs and by `InodeSyncStream.loadDirectoryMetadata`.

## Risks
`mDefaultAcl` defaults to null, so consumers must distinguish absent default ACL from empty default ACL. As with other contexts, builder-backed options are mutable. Using `create` rather than `mergeFrom` can skip master defaults. Metadata-load callers must set UFS-derived fields consistently to avoid mismatched Alluxio/UFS metadata.

## Test signals
Tests should cover default merging, operation-id override, default ACL copying/immutability, metadata-load directory creation, mount-point creation, and null versus empty default ACL behavior.
