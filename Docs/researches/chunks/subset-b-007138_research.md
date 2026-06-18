# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.0.xml lines 6133-12073

## Scope

This chunk covers a JDiff public API description for Hadoop Common filesystem APIs. The range starts at the tail of `org.apache.hadoop.fs.CreateFlag`, then fully describes `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`, and ends partway through `FilterFileSystem` after its `getUsed()` method. Because this is generated API metadata rather than Java source, it exposes signatures, inheritance, visibility, deprecation state, exceptions, and Javadoc contracts, but not method bodies.

## Purpose

The APIs in this chunk define Hadoop's core filesystem abstraction layer. They let applications address multiple URI-backed filesystems through `Path`, create/read/write/delete data, inspect metadata, manage permissions, ACLs, xattrs, symlinks, snapshots, checksums, storage policies, and statistics, and bridge local disk with remote filesystems.

`FileContext` is the newer context-oriented API over `AbstractFileSystem`: it carries default filesystem resolution, working directory, umask, and user identity. `FileSystem` is the older and still central abstract class that concrete implementations subclass. `FilterFileSystem` wraps another `FileSystem` and forwards operations. `FileStatus` and `FileChecksum` are serializable metadata/value objects. `FileUtil` supplies static helpers for local files, copies, deletion, archives, shell path handling, permissions, classpath jar expansion, and filesystem comparison.

## Important APIs, Types, and Functions

### Creation, checksums, and exceptions

- `CreateFlag` is only partially visible here, but the chunk includes documented valid flag combinations such as `CREATE`, `APPEND`, `OVERWRITE`, and combinations used by create/append streams.
- `FileAlreadyExistsException` extends `IOException` and has empty and message constructors. Its contract is specifically for operations where the target exists and overwrite was not configured.
- `FileChecksum` is an abstract `Writable` representing a file checksum. Implementations must provide `getAlgorithmName()`, `getLength()`, and `getBytes()`. The base API also exposes `getChecksumOpt()`, `equals(Object)`, and `hashCode()`, with equality defined over both algorithm and checksum bytes.

### `FileContext`

`FileContext` exposes a high-level filesystem namespace context over `AbstractFileSystem`.

- Factory methods create contexts from an `AbstractFileSystem`, default configuration, explicit `URI`, explicit `Configuration`, or the local filesystem. Failures are modeled as `UnsupportedFileSystemException`, `IOException`, or runtime failures during instantiation/login.
- Path state methods include `setWorkingDirectory(Path)`, `getWorkingDirectory()`, `getHomeDirectory()`, `getUgi()`, `getUMask()`, `setUMask(FsPermission)`, `makeQualified(Path)`, `resolvePath(Path)`, protected `resolve(Path)`, and protected `resolveIntermediate(Path)`.
- Core namespace operations include `create(Path, EnumSet<CreateFlag>, Options.CreateOpts...)`, `mkdir(Path, FsPermission, boolean)`, `delete(Path, boolean)`, `open(Path)` and `open(Path, int)`, `truncate(Path, long)`, `setReplication(Path, short)`, `rename(Path, Path, Options.Rename...)`, permission/owner/time setters, checksums, and checksum verification toggles.
- Metadata and listing APIs include `getFileStatus(Path)`, `getFileLinkStatus(Path)`, `getLinkTarget(Path)`, `getFsStatus(Path)`, `listStatus(Path)`, `listLocatedStatus(Path)`, and `listCorruptFileBlocks(Path)`.
- Symlink creation is documented with URI qualification rules for target and link paths, including how qualified and relative targets are interpreted.
- Security and metadata extension APIs cover ACL modification/replacement/removal/query, xattr set/get/list/remove with namespaced names such as `user.attr`, snapshots, and storage policies.
- Static statistics methods expose per-filesystem statistics keyed by URI scheme/authority: `getStatistics(URI)`, `clearStatistics()`, `printStatistics()`, and `getAllStatistics()`.
- Public constants include `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`. The docs note that `DEFAULT_PERM` previously applied executable permissions to files and is retained for compatibility after HADOOP-9155.

### `FileStatus`

`FileStatus` is a `Writable` and `Comparable` metadata object.

- Constructors cover empty/default status, basic size/directory/replication/block-size/time/path fields, full permission/owner/group/path forms, optional symlink target, and a copy constructor.
- Accessors expose length, file/directory/symlink type, block size, replication, modification/access times, permissions, encryption flag, owner, group, path, and symlink target.
- Mutators include `setPath`, protected `setPermission`, protected `setOwner`, protected `setGroup`, and public `setSymlink`.
- Serialization and identity APIs are `write(DataOutput)`, `readFields(DataInput)`, `compareTo(Object)`, `equals(Object)`, `hashCode()`, and `toString()`.
- `isDir()` is deprecated in favor of explicit `isFile()`, `isDirectory()`, and `isSymlink()`.

### `FileSystem`

`FileSystem` extends `Configured` and implements `Closeable`. It is the main abstract base for filesystem implementations.

- Static resolution APIs include `get(Configuration)`, `get(URI, Configuration)`, `getDefaultUri(Configuration)`, `setDefaultUri(...)`, `getLocal(Configuration)`, `newInstance(...)`, `newInstanceLocal(Configuration)`, `closeAll()`, `closeAllForUGI(UserGroupInformation)`, `getFileSystemClass(String, Configuration)`, global statistics accessors, global storage statistics, and symlink enablement.
- Identity and URI methods include `initialize(URI, Configuration)`, `getScheme()`, abstract `getUri()`, `getCanonicalUri()`, `canonicalizeUri(URI)`, `getDefaultPort()`, `getFSofPath(Path, Configuration)`, `getCanonicalServiceName()`, deprecated `getName()`, and deprecated `getNamed(String, Configuration)`.
- Core data operations include many overloaded `create(...)` methods, abstract `open(Path, int)`, abstract `append(Path, int, Progressable)`, `createNonRecursive(...)`, `primitiveCreate(...)`, `createNewFile(Path)`, `concat(Path, Path[])`, `truncate(Path, long)`, abstract `rename(Path, Path)`, protected rename with `Options.Rename`, abstract `delete(Path, boolean)`, and deprecated `delete(Path)`.
- Directory and listing operations include `mkdirs(...)`, protected `primitiveMkdir(...)`, abstract `listStatus(Path)`, filtered/list-of-path overloads, `globStatus(...)`, `listLocatedStatus(...)`, protected filtered located listing, `listStatusIterator(Path)`, `listFiles(Path, boolean)`, and corrupt block iteration.
- Metadata operations include block locations, server defaults, `resolvePath`, replication, status, content summary, quota usage, existence/type checks, home/working directory, local/remote copy helpers, local output staging/completion, used space, default block size/replication, checksum operations, checksum read/write toggles, filesystem status, permissions, owner, times, symlinks, ACLs, xattrs, snapshots, storage policies, trash roots, and builder entry points `createFile(Path)` and `appendFile(Path)`.
- Constants include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and the per-instance `statistics` object.

### `FileUtil`

`FileUtil` is a static helper collection for local and Hadoop filesystem file processing.

- Path conversion and deletion helpers include `stat2Paths(...)`, `fullyDeleteOnExit(File)`, `fullyDelete(...)`, `fullyDeleteContents(...)`, and `fullyDelete(File, boolean)`.
- Copy helpers bridge `FileSystem` and local `File`: multiple `copy(...)` overloads, `copyMerge(...)`, delete-source flags, overwrite flags, and `Configuration` propagation.
- Local utility helpers include `readLink(File)`, `makeShellPath(...)`, `getDU(File)`, `unZip(...)`, `unTar(...)`, `symLink(...)`, `chmod(...)`, `setOwner(...)`, readable/writable/executable setters and checks, `setPermission(File, FsPermission)`, temp-file creation, `replaceFile(...)`, and filtered file listing.
- Classpath helpers create jars with expanded classpaths and enumerate jars in directories, optionally using local path handling.
- `compareFs(FileSystem, FileSystem)` compares filesystem identity, and `SYMLINK_NO_PRIVILEGE` represents a symlink failure mode.

### `FilterFileSystem`

The visible part of `FilterFileSystem` shows a wrapper implementation around another `FileSystem`.

- Constructors support an empty wrapper or an immediately supplied raw filesystem.
- `getRawFileSystem()` exposes the wrapped instance.
- URI/path methods include `initialize`, `getUri`, `getCanonicalUri`, `canonicalizeUri`, `makeQualified`, and protected `checkPath`.
- Forwarded operations visible in this chunk include block locations, resolve, open, append, concat, create, `createNonRecursive`, replication, rename, truncate, delete, listing, corrupt block listing, located/status iterators, home/working directory, status, mkdirs, local copy helpers, local output staging/completion, and `getUsed()`.

## Control Flow

The documented control flow is layered around path resolution, filesystem dispatch, operation execution, and metadata/result wrapping.

For `FileContext`, callers first construct a context from configuration, a default URI, an explicit `AbstractFileSystem`, or the local filesystem. Relative paths are resolved through the context's working directory, slash-relative paths through the default filesystem, and fully qualified paths through their own scheme/authority. Operations then locate the target `AbstractFileSystem` with `getFSofPath`, apply context state such as umask, and dispatch to the underlying filesystem. The Javadoc explicitly distinguishes client-side context defaults from server-side filesystem defaults such as home directory, initial working directory, replication, block size, buffer size, data transfer encryption, and checksum parameters.

For `FileSystem`, callers generally obtain cached instances through `get(...)` or uncached instances through `newInstance(...)`. Concrete implementations provide abstract methods such as `open`, `create`, `append`, `rename`, `delete`, `listStatus`, `setWorkingDirectory`, `getWorkingDirectory`, and `getFileStatus`; the base class supplies convenience overloads, default fallbacks, validation wrappers, recursive/listing utilities, glob expansion, local copy flows, and optional-operation stubs. Builder methods (`createFile`, `appendFile`) expose a newer fluent entry point over the same create/append semantics.

The create path is especially overloaded. Public APIs accept booleans, `EnumSet<CreateFlag>`, permissions, buffer sizes, replication, block sizes, progress callbacks, and checksum options. `FileContext` applies umask before calling lower-level primitives, while `FileSystem` exposes `primitiveCreate` and `primitiveMkdir` for the transition from `FileSystem` to `FileContext`. Non-recursive creation variants fail when a parent directory is missing. `createNewFile` is documented as not atomic in the default implementation.

Listing control flow can be eager or lazy. `listStatus` returns arrays, filtered overloads apply `PathFilter`, `globStatus` expands shell-style patterns and sorts results by path/name, `listStatusIterator` returns on-demand `RemoteIterator<FileStatus>`, `listLocatedStatus` includes block locations for files, and `listFiles` traverses files recursively or non-recursively.

`FilterFileSystem` control flow is wrapper-style: path checks, URI canonicalization, stream creation, metadata calls, and mutation operations are forwarded to the wrapped raw filesystem. The raw filesystem remains observable through `getRawFileSystem()`, so wrapper subclasses can add behavior without reimplementing every backend operation.

## State and Persistence Behavior

The persistent state represented by these APIs is filesystem namespace state: files, directories, lengths, block metadata, replication, permissions, ownership, access/modification times, symlinks, ACLs, xattrs, snapshots, storage policies, checksums, and trash locations. The XML does not include concrete persistence code, but the contracts make clear which operations mutate remote or local filesystem state.

Client-side state is also significant:

- `FileContext` holds default filesystem identity, working directory, umask, and `UserGroupInformation`. Its working directory model is textual prefixing rather than a Unix-like inode-bound current directory, and the docs say `setWorkingDirectory()` does not follow symlinks.
- `FileSystem` holds `Configuration`, cached instances, shutdown-hook behavior, delete-on-exit registrations, per-filesystem `Statistics`, and storage statistics. `deleteOnExit` persists only in process memory until `close()` or clean JVM shutdown, and the docs warn that shutdown is not guaranteed and can be slow for many paths or remote/object stores.
- `FileStatus` and `FileChecksum` are `Writable`, so they can be serialized over RPCs, stored in job metadata, or passed across process boundaries.
- `FileUtil` helpers mutate local disk state for deletion, archive extraction, temporary files, replacement, permissions, ownership, and symlinks.

Several operations are optional or implementation-dependent. Append, concat, truncate, checksums, symlinks, snapshots, ACLs, xattrs, storage policies, corrupt block listings, and replication may be unsupported, no-op-like, non-atomic, or backed by filesystem-specific semantics. Rename atomicity is explicitly implementation-dependent, and the default protected rename with options is documented as non-atomic.

## Dependencies and Integration Points

These APIs are central integration points for the rest of Hadoop Common and downstream filesystems.

- Configuration and identity: `org.apache.hadoop.conf.Configuration`, `Configured`, `UserGroupInformation`, delegation `Token`, and canonical service names.
- Filesystem model: `Path`, `AbstractFileSystem`, `LocalFileSystem`, `FsStatus`, `FsServerDefaults`, `BlockLocation`, `BlockStoragePolicySpi`, `ContentSummary`, `QuotaUsage`, `StorageStatistics`, and `GlobalStorageStatistics`.
- Streams and iteration: `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `RemoteIterator`, `Progressable`, `Closeable`, `IOException`, `FileNotFoundException`, and Hadoop-specific filesystem exceptions.
- Security and metadata: `FsPermission`, `AclStatus`, ACL entry lists, xattr name/value maps, `Options.ChecksumOpt`, `Options.CreateOpts`, `Options.Rename`, and `XAttrSetFlag`-style enum sets.
- Serialization and comparison: Hadoop `Writable`, Java `Comparable`, and `DataInput`/`DataOutput`.
- Local platform integration: `java.io.File`, shell path conversion, symlink/permission/ownership changes, archive extraction, and classpath jar generation.

The API surface is also a compatibility contract for HDFS, LocalFileSystem, object-store connectors, viewfs, checksum wrappers, encryption-aware filesystems, and test/mock filesystems. Any concrete `FileSystem` must honor the abstract methods and the documented behavior of convenience methods that depend on them.

## Risks and Edge Cases

- This chunk is API metadata only. Research about implementation behavior must be treated as contract-level analysis unless verified against the Java source.
- Path qualification is subtle. `FileContext` supports fully qualified URIs, slash-relative paths resolved against the default filesystem, and working-directory-relative paths; relative paths with schemes are illegal.
- `setWorkingDirectory()` in `FileContext` does not follow symlinks. Code expecting Unix current-directory semantics can resolve later paths differently than expected.
- Umask handling differs between `FileContext` and lower-level `FileSystem` methods. The presence of `primitiveCreate` and `primitiveMkdir` indicates compatibility risk when implementing custom filesystems.
- `createNewFile()` is explicitly non-atomic in the default implementation, so it is unsafe as a distributed lock primitive unless overridden with stronger semantics.
- Rename semantics are not uniformly atomic. The option-based default implementation is documented as non-atomic, while concrete filesystems may differ.
- `deleteOnExit` is process-local and best-effort. It can lengthen shutdown, fail under remote connectivity problems, and does not guarantee cleanup on abnormal JVM termination.
- Many methods are optional operations with default unsupported behavior or weak default behavior. Tests must distinguish unsupported features from incorrect results.
- `setReplication()` default behavior may return true even when replication is unsupported, potentially masking ineffective replication changes on non-HDFS stores.
- Listing order is generally not guaranteed for `listStatus`, `listStatusIterator`, or `listFiles`, while `globStatus` documents sorted results. Callers should not rely on directory iteration ordering unless the specific API promises it.
- XAttr APIs require namespace prefixes such as `user.` and return only attributes visible to the logged-in user, so authorization and filtering affect apparent metadata.
- ACL replacement with `setAcl` must include base user/group/other entries for permission-bit compatibility.
- `FileStatus` contains deprecated `isDir()` alongside the newer explicit type checks; older callers can miss symlink distinctions.
- `FileUtil` destructive helpers such as recursive delete, replace, chmod/chown, unzip/untar, and symlink creation cross local platform boundaries and need careful failure handling in tests and tooling.
- `FilterFileSystem` exposes its raw filesystem, so wrappers cannot assume strict encapsulation. Any added behavior can be bypassed by code that unwraps the raw instance.

## Test Signals

Useful tests around the APIs described in this chunk should emphasize contract behavior across at least local and distributed/mock filesystems:

- Path resolution tests for `FileContext`: fully qualified paths, slash-relative paths, working-directory-relative paths, illegal relative-with-scheme paths, symlink resolution, and `makeQualified`.
- Creation tests for all major `CreateFlag` combinations, overwrite rejection via `FileAlreadyExistsException`, create-parent behavior, non-recursive create failures, permissions after umask, checksum options, and progress callbacks.
- Metadata tests for `FileStatus` serialization, equality/comparison, symlink fields, encryption flag, default permission/owner/group behavior, and deprecated `isDir()` compatibility.
- Listing tests for missing paths, file-vs-directory inputs, filters, glob patterns, sorted glob output, unspecified normal listing order, lazy iterator error propagation, located status block locations, and recursive `listFiles`.
- Mutation tests for rename with and without overwrite, directory/file mismatch failures, non-empty destination directory behavior, truncate return value semantics, delete recursive flags, owner/permission/time setters, and replication on filesystems that do and do not support replication.
- Optional feature tests for append, concat, checksums, symlinks, ACLs, xattrs, snapshots, storage policies, corrupt block iteration, trash roots, and storage statistics, checking both successful implementations and documented unsupported paths.
- Lifecycle tests for cached `FileSystem.get(...)` versus `newInstance(...)`, `closeAll`, `closeAllForUGI`, delete-on-exit processing/cancellation, statistics collection/clear/print, and shutdown-hook priority behavior.
- `FileUtil` tests for recursive deletion, delete-on-exit registration, local/Hadoop copy combinations, copy-merge, archive extraction, shell path formatting, disk usage, temp file creation, file replacement, permission toggles, symlink failure codes, classpath jar creation, jar directory expansion, and `compareFs`.
- `FilterFileSystem` tests should verify forwarding of URI/path operations, stream operations, metadata/listing/mutation calls, raw filesystem exposure, and wrapper behavior when the underlying filesystem throws `IOException`.
