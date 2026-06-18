# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/CompleteFileContext.java

## Purpose
`CompleteFileContext` wraps `CompleteFilePOptions` and carries extra master-only state for completing files, including operation time, UFS status, and whether completion comes from metadata loading.

## Important APIs, types, and functions
It extends `OperationContext<CompleteFilePOptions.Builder, CompleteFileContext>`. Static constructors are `create`, `mergeFrom`, and `defaults`. Extra methods include `setMetadataLoad`, `isMetadataLoad`, `getUfsStatus`, `setUfsStatus`, `getOperationTimeMs`, `setOperationTimeMs`, and an override of `getOperationId` that reads common proto operation id first.

## Control flow
The constructor initializes operation time to current system time and UFS status to null. `mergeFrom` overlays caller options on `FileSystemMasterOptions.completeFileDefaults()`. Metadata sync uses the context with UFS length/status and metadata-load flag after creating a file from UFS metadata.

## State and persistence behavior
The context influences persisted completed-file metadata, including UFS length, operation time, metadata-load flag, and common TTL/operation options. It does not journal directly; callers pass it into master internals that journal completion.

## Dependencies and integration points
It depends on complete-file protos, `FileSystemMasterOptions`, `UfsStatus`, `OperationId`, and `OperationContext`. `InodeSyncStream.loadFileMetadataInternal` is a key integration point.

## Risks
`toString()` calls `mUfsStatus.toString()` without a null check, so logging a default context can throw `NullPointerException`. Operation time uses wall-clock time by default, while metadata loads may override with UFS last-modified time. Correct operation-id propagation depends on common options being set.

## Test signals
Tests should cover default/merged options, metadata-load flag, operation-id override, UFS status handling, and the null-status `toString()` edge case.
