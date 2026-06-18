# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/viewfs/ChRootedFs.java

`ChRootedFs` is the `AbstractFileSystem` counterpart to `ChRootedFileSystem`. It wraps an `AbstractFileSystem` and exposes a filesystem rooted below the raw filesystem root. It is used by the newer `ViewFs` API path rather than the older `FileSystem`-based `ViewFileSystem` path.

The key APIs mirror the `FileSystem` wrapper: `fullPath(Path)` prefixes an absolute checked path with `chRootPathPartString`; `stripOutRoot(Path)` removes the chroot prefix from a qualified target path; `getResolvedQualifiedPath(Path)` qualifies a path after chroot expansion; and `getMyFs()` exposes the raw `AbstractFileSystem`. The constructor validates the root against the raw filesystem, derives the URI path with `myFs.getUriPath(theRoot)`, and constructs a URI containing the chrooted path.

Most methods are direct delegations after path expansion: `createInternal`, `delete`, `open`, `mkdir`, `renameInternal`, file status, located listing, ACL/xattr, snapshots, checksums, storage policies, checksum settings, symlink creation, and delegation token retrieval. State is in-memory only: raw filesystem reference, URI, chroot path, and string prefix. Durable data and metadata changes happen in the wrapped filesystem.

Dependencies are Hadoop `AbstractFileSystem`, `Path`, `FileStatus`, `Token`, ACL/xattr/storage policy APIs, and `Options.ChecksumOpt`. Integration is with `ViewFs` and `InodeTree<AbstractFileSystem>` implementations.

Risks include differences from `ChRootedFileSystem`: `satisfyStoragePolicy(Path)` and `getStoragePolicy(Path)` delegate some paths without `fullPath`, so tests should verify intended behavior. Symlink semantics are also subtle because the target is chrooted but the link argument is intentionally not rewritten. Test signals should include root and non-root chroots, symlinks, rename across same chroot, ACL/xattr, snapshot paths, and storage policy path handling.
