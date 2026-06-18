# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFsFileStatus.java

Purpose: Wraps a target filesystem `FileStatus` while replacing only the visible path with the corresponding viewfs-qualified path. This works around status implementations, especially local filesystem status objects, whose owner/group resolution may depend on the original target status object.

Important APIs and types: Package-private `ViewFsFileStatus extends FileStatus` stores `myFs` and `modifiedPath`. It overrides metadata accessors such as length, file/directory/symlink flags, block size, replication, modification/access time, permissions, owner, group, path, `setPath()`, and `getSymlink()`.

Control flow: Construction captures the original status and new path. Every metadata call delegates to `myFs` except `getPath()`/`setPath()`, which read and mutate `modifiedPath`. Equality and hash code defer to `FileStatus` superclass behavior.

State and persistence: It is a transient adapter with no persistence. State is the referenced status plus mutable display path. Mutating `setPath()` affects only the wrapper path, not the target filesystem object.

Dependencies and integration points: Used by `ViewFs.getFileStatus()`, `ViewFs.listStatus()`, and `WrappingRemoteIterator` to present target results under viewfs. It depends on `FileStatus`, `Path`, and `FsPermission`.

Risks: Because equality and comparison behavior comes from `FileStatus`, wrapper identity depends on superclass use of overridden accessors. If new `FileStatus` fields are added, this wrapper may need more delegates. The target status object remains live, so lazy target-specific behavior can still execute.

Test signals: ViewFs status/listing tests should assert path qualification, owner/group behavior on local targets, symlink preservation, and stable behavior after `setPath()`.
