# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ViewFs.java

Purpose: Implements the `viewfs://` `AbstractFileSystem` client-side mount table. It composes multiple target file systems behind one namespace, builds an in-memory `InodeTree<AbstractFileSystem>` from Hadoop configuration, and delegates file operations to `ChRootedFs` targets while presenting paths in the viewfs namespace.

Important APIs and types: Main public surface is the `ViewFs` class, `MountPoint`, `getMountPoints()`, `getDelegationTokens()`, and `AbstractFileSystem` overrides for create, delete, status, listing, mkdir, open, truncate, rename, symlink, ACL, xattr, snapshot, and storage policy operations. Internal helpers include `readOnlyMountTable()`, `WrappingRemoteIterator`, and `InternalDirOfViewFs`.

Control flow: Construction reads authority-specific mount table configuration, creates target `AbstractFileSystem` instances under the creating UGI, wraps them as `ChRootedFs`, and creates `InternalDirOfViewFs` objects for internal mount directories. Most operations resolve `getUriPath(path)` through `fsState.resolve()`, then call the same operation on `res.targetFileSystem` with `res.remainingPath`. Status and listing paths are rewritten to qualified viewfs paths with `ViewFsFileStatus` or `ViewFsLocatedFileStatus`.

State and persistence: Runtime state is client-local: `creationTime`, creator `ugi`, `config`, cached `homeDir`, static `showMountLinksAsSymlinks`, `renameStrategy`, and the in-memory `fsState`. Persistent filesystem mutations occur only in target filesystems or the configured root fallback filesystem. Internal mount table nodes are read-only unless fallback handling redirects create/mkdir/rename/block-location work.

Dependencies and integration points: Depends on `InodeTree`, `ChRootedFs`, `Constants`, `ConfigUtil`, `ViewFileSystem.RenameStrategy`, Hadoop `AbstractFileSystem`, `FileContext`, ACL/xattr/snapshot/storage policy APIs, delegation token APIs, and UGI. It integrates with viewfs tests and HDFS-local viewfs contract tests.

Risks: Path rewriting is subtle for chrooted targets, fallback paths, internal directories, and mount links shown as symlinks versus resolved objects. Rename is high risk because it may cross mount points and relies on configured strategy checks. Internal directory mutators must consistently reject changes unless fallback is present. The static symlink-display flag is process-wide and can be surprising with multiple configurations.

Test signals: `ViewFsBaseTest`, `TestViewFsLocalFs`, `TestViewFsHdfs`, fallback tests, ACL/xattr/truncate/storage-policy tests, delegation-token tests, and rename-strategy tests should cover resolution, listing, read-only mount table behavior, fallback precedence, path qualification, and target delegation.
