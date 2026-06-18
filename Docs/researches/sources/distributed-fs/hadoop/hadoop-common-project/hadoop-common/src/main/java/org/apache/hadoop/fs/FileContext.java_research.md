# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileContext.java

## Purpose

`FileContext` is Hadoop's public, stable file-system facade over `AbstractFileSystem`. It models process-like file-system state: a default filesystem for slash-relative paths, a fully qualified working directory for working-directory-relative paths, a configurable umask, the current `UserGroupInformation`, symlink-resolution behavior from configuration, and a tracing handle. It exposes high-level operations for create/open/delete/rename/list/status, metadata mutation, symlinks, ACLs, xattrs, snapshots, storage policies, delegation tokens, server defaults, path capabilities, async open builders, and multipart upload builders.

The class is intentionally different from `FileSystem`: each factory call creates a new `FileContext` except the underlying filesystem/statistics caches in lower layers. It is the API point that normalizes user paths, resolves symlinks and mount points, and dispatches to the correct `AbstractFileSystem` implementation.

## Important APIs and types

- Factory methods: `getFileContext()`, `getFileContext(Configuration)`, `getFileContext(URI)`, `getFileContext(URI, Configuration)`, `getFileContext(AbstractFileSystem, Configuration)`, and local filesystem variants. These construct a context using `fs.defaultFS` or an explicit URI.
- Path-state APIs: `setWorkingDirectory`, `getWorkingDirectory`, `getHomeDirectory`, `makeQualified`, `resolvePath`, `getUMask`, `setUMask`, `getUgi`, and the test-only `getDefaultFileSystem`.
- Core IO and namespace APIs: `create(Path, EnumSet<CreateFlag>, CreateOpts...)`, builder-style `create(Path)`, `mkdir`, `delete`, `open`, `open(Path, int)`, `truncate`, `setReplication`, `rename`, `getFileStatus`, `getFileLinkStatus`, `getLinkTarget`, `getFileBlockLocations`, `getFsStatus`, `listStatus`, `listLocatedStatus`, `listCorruptFileBlocks`, `deleteOnExit`, and `msync`.
- Metadata APIs: `setPermission`, `setOwner`, `setTimes`, `getFileChecksum`, `setVerifyChecksum`, and `access`.
- Symlink APIs: `createSymlink`, `resolve`, `resolveIntermediate`, and symlink target qualification in `getFileLinkStatus`.
- `Util` inner class: convenience layer for `exists`, recursive `getContentSummary`, array-returning `listStatus`, filtered listing, recursive `listFiles`, globbing through `Globber`, and recursive/cross-filesystem `copy`.
- Security and cluster integration APIs: `getDelegationTokens`, `resolveAbstractFileSystems`, and static filesystem statistics forwarding methods.
- ACL/XAttr APIs: `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, `getAclStatus`, `setXAttr`, `getXAttr`, `getXAttrs`, `removeXAttr`, and `listXAttrs`.
- Snapshot and storage policy APIs: `createSnapshot`, `renameSnapshot`, `deleteSnapshot`, `satisfyStoragePolicy`, `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Newer builder/capability APIs: `openFile(Path)` returning `FutureDataInputStreamBuilder`, `hasPathCapability`, `getServerDefaults`, and `createMultipartUploader`.

## Control flow

Most public methods follow a common path: validate or normalize the input path with `fixRelativePart`, wrap the target operation in an `FSLinkResolver`, and call `resolve(this, absPath)` so symlinks/mount points can redirect the operation to the correct `AbstractFileSystem`. `getFSofPath` first checks whether a path belongs to the context's `defaultFS`; otherwise it instantiates another `AbstractFileSystem` under the captured `UserGroupInformation`.

Construction captures current user, tracer, default filesystem, initial working directory, and symlink policy. If the default filesystem has an initial working directory, that is used; otherwise the default filesystem home directory becomes the working directory.

Create flow applies umask before delegation. `create(Path, flags, opts...)` extracts a supplied `CreateOpts.Perms` or defaults to `FILE_DEFAULT_PERM`, applies `FsCreateModes.applyUMask`, replaces the option, then delegates to `AbstractFileSystem.create`. The nested output-stream builder collects block size, buffer size, replication, permission, checksum, progress, and recursive-parent options before calling the same `create` method.

Rename is special because it has two paths. It resolves the source and destination filesystems directly, rejects cross-`AbstractFileSystem` renames, and calls `srcFS.rename`. If symlink resolution fails, it resolves intermediate source components, then resolves the destination through `FSLinkResolver`.

`Util.listFiles` implements a depth-first iterator using a stack of `RemoteIterator<LocatedFileStatus>`. It yields only files; directories are traversed when `recursive` is true, and symlinks are resolved enough to decide whether to traverse or yield their targets.

`Util.copy` qualifies source and destination, validates overwrite/subdirectory constraints, recurses through directories, and copies files by opening the source via `openFile` with whole-file and length hints, then streaming to `create` using `IOUtils.copyBytes`. Optional `deleteSource` deletes the source recursively after copy.

## State and persistence behavior

Instance state is small but important: `defaultFS`, `workingDir`, `umask`, `conf`, `ugi`, `resolveSymlinks`, `tracer`, and the singleton `util` facade. The underlying namespace, file data, ACLs, xattrs, snapshots, storage policies, checksums, tokens, server defaults, and statistics are persisted or owned by the delegated `AbstractFileSystem` implementations.

`DELETE_ON_EXIT` is static process state keyed by `FileContext` identity. `deleteOnExit` verifies existence, installs `FileContextFinalizer` as a JVM shutdown hook on first use, stores paths in a per-context `TreeSet`, and `processDeleteOnExit` later calls `delete(path, true)` for each path while logging and ignoring failures.

Statistics are not stored in `FileContext`; static methods forward to `AbstractFileSystem` statistics keyed by URI. `getDelegationTokens` resolves all filesystems touched by a path, including symlink hops, then aggregates tokens from each.

## Dependencies and integration points

This class integrates with nearly every common filesystem API in `org.apache.hadoop.fs`: `Path`, `AbstractFileSystem`, `FSLinkResolver`, `FsLinkResolution`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `Globber`, `RemoteIterator`, `ContentSummary`, `FileChecksum`, `MultipartUploaderBuilder`, and open/create option classes. It also depends on permission and security packages (`FsPermission`, `FsCreateModes`, `FsAction`, ACL types, `UserGroupInformation`, delegation `Token`) and on configuration/tracing utilities.

The `openFile` builder bridges old synchronous `open` behavior with newer async/builder-style APIs by packaging `OpenFileParameters` and calling `AbstractFileSystem.openFileWithOptions`. `hasPathCapability`, `getServerDefaults`, and `createMultipartUploader` use `FsLinkResolution.resolve`, a newer lambda-based resolver.

## Risks and edge cases

- `fixRelativePart` prefixes relative paths with the current working directory but does not fully qualify slash-relative paths; later resolver calls must complete filesystem selection.
- `setWorkingDirectory` checks that the target exists and is not a file, but it stores a `new Path(workingDir, newWDir)` value rather than an inode-like resolved directory. This matches the documented distributed semantics but can surprise Unix-minded callers.
- `deleteOnExit` stores paths as passed, not a fully qualified resolved copy. Later working-directory or filesystem changes could affect ambiguous relative paths.
- `Util.getContentSummary` recursively walks the namespace client-side. It is not atomic and can be expensive or inconsistent under concurrent changes.
- `Util.copy` is explicitly non-atomic and can partially complete. Directory copy recursion plus optional source deletion needs failure tests.
- `checkDependencies` depends on `isSameFS`; the implementation returns true for same scheme unless both authorities are non-null and equal, which is counterintuitive for a method named "isSameFS" and may weaken self/subdirectory-copy detection for fully matching authorities.
- Storage policy methods `satisfyStoragePolicy`, `setStoragePolicy`, and `unsetStoragePolicy` compute `absF`/resolver path `p` but delegate using the original `path`/`src` variable, which is a risk for relative paths, symlink resolution, or mounted filesystems.
- `getFileLinkStatus` qualifies symlink targets only when the returned status is a symlink; callers must still handle dangling or cross-filesystem links.
- Access checks are documented as TOCTOU-prone and should not be used as an authorization substitute for executing the intended operation.

## Test signals

Strong tests should cover relative, slash-relative, fully qualified, and illegal scheme-relative paths; working-directory changes; umask application for file and directory creation; symlink resolution for final and intermediate components; cross-filesystem rename rejection; delete-on-exit registration and cleanup; recursive listing through directories and symlinks; glob null-vs-empty behavior; copy overwrite, directory recursion, self/subdirectory rejection, and delete-source behavior; ACL and xattr delegation; snapshot/storage-policy delegation with relative and symlinked paths; async `openFile` option propagation; `hasPathCapability` validation; delegation token aggregation across symlinked filesystems; and statistics forwarding/clearing.
