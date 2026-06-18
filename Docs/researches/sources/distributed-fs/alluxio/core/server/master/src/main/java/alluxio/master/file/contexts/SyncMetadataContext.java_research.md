# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/SyncMetadataContext.java

Purpose: wraps `SyncMetadataPOptions` for explicit metadata sync requests. It is a thin context used to merge request options with master sync defaults.

Important APIs and types: `create`, `mergeFrom`, and `defaults` construct contexts using `FileSystemOptionsUtils.syncMetadataDefaults`. `toString` renders the built protobuf options.

Control flow: RPC handling builds the context, then higher-level metadata-sync code chooses descendant type, directory load type, sync interval, and async behavior from the options. This wrapper does not own task orchestration; that happens in the `mdsync` package.

State and persistence behavior: no direct persistence. Options drive the background task group that may create, update, or delete inode metadata through `DefaultSyncProcess`.

Dependencies and integration points: depends on sync metadata protobufs, configuration, file-system option utilities, and `OperationContext`. It is a front door into `DefaultSyncProcess.syncPath`.

Risks: the Javadoc still references `ExistsPOptions` in `mergeFrom`, which is documentation drift. Any new sync-specific runtime flags need to be added here or in the mdsync task classes.

Test signals: default merging, sync metadata RPC option handling, and end-to-end sync task launch are the relevant signals.
