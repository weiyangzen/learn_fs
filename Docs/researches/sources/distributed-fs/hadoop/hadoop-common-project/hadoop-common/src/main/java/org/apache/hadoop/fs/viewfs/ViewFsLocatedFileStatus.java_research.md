# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsLocatedFileStatus.java

Purpose: Provides the located-status equivalent of `ViewFsFileStatus`, preserving target `LocatedFileStatus` metadata and block locations while substituting the visible viewfs path.

Important APIs and types: Package-private `ViewFsLocatedFileStatus extends LocatedFileStatus` stores a target `LocatedFileStatus` and mutable `modifiedPath`. It delegates all normal file metadata, symlink get/set, and `getBlockLocations()` while overriding `getPath()` and `setPath()`.

Control flow: Created by `ViewFs.listLocatedStatus()` through `WrappingRemoteIterator`. Iterator results from the target filesystem are transformed one by one into wrappers whose paths are reconstructed from the resolved viewfs path and the target suffix.

State and persistence: No persistent state. It retains the target located status and a mutable display path. Block locations are target-provided and are not rewritten.

Dependencies and integration points: Integrates with `ViewFs.listLocatedStatus()` and Hadoop `LocatedFileStatus` consumers such as file scanners and block-location-aware tools.

Risks: Block locations may expose target filesystem details while paths expose viewfs paths, so callers must tolerate that split. As with `ViewFsFileStatus`, new `LocatedFileStatus` fields can require delegate updates.

Test signals: Tests should cover `listLocatedStatus()` path rewriting, block location preservation, symlink status, equality/hash behavior, and listing through mount links and non-internal target directories.
