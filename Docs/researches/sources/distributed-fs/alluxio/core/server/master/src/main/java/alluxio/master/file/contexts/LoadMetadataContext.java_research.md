# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/contexts/LoadMetadataContext.java

Purpose: wraps `LoadMetadataPOptions` for explicit metadata loading from UFS into Alluxio namespace and optionally carries a pre-fetched `UfsStatus`.

Important APIs and types: `create`, `mergeFrom`, and `defaults` handle construction. `getUfsStatus` and `setUfsStatus` attach UFS status information to the context.

Control flow: load-metadata callers merge request options over `FileSystemOptionsUtils.loadMetadataDefaults`, optionally set a `UfsStatus`, and pass the context into master metadata loading logic. The context's `toString` includes both proto options and UFS status for diagnostics.

State and persistence behavior: the context is transient, but the attached `UfsStatus` can become source data for persisted inode metadata such as file or directory type, owner, group, mode, length, and fingerprint.

Dependencies and integration points: depends on `LoadMetadataPOptions`, UFS status types, configuration defaults, and `OperationContext`. It integrates with file-master load-metadata paths and overlaps conceptually with metadata sync context classes.

Risks: `mUfsStatus` is nullable; callers that expect preloaded status must check. Stale UFS status attached to a context can lead to incorrect metadata if reused after UFS changes.

Test signals: tests should cover default merging, status propagation, null status behavior, and metadata-load creation from status for both files and directories.
