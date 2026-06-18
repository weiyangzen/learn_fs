# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.8.0.xml lines 6053-11998

## Purpose

This chunk is generated JDiff API metadata for a major part of Hadoop Common 2.8.0's `org.apache.hadoop.fs` public contract. It starts inside the `FileContext` API, then covers `FileStatus`, the core abstract `FileSystem` base class, local file utility helpers, `FilterFileSystem`, filesystem constants, data input/output stream wrappers, filesystem error and input-stream abstractions, and `FsServerDefaults`.

The XML is not implementation code. Its value is the public compatibility surface: type names, inheritance, implemented interfaces, constructors, method signatures, checked exceptions, field names, deprecation state, and Javadocs describing expected semantics.

## API Inventory

### `org.apache.hadoop.fs.FileContext` tail

- The chunk begins in `FileContext` operations for opening files, truncating, changing replication, rename with `Options.Rename[]`, permission/owner/time mutation, file checksums, checksum verification, status and link status, symlink target lookup, filesystem status, symlink creation, directory/status iteration, corrupt block listing, located status listing, delete-on-exit registration, path resolution, and statistics.
- ACL APIs include `modifyAclEntries`, `removeAclEntries`, `removeDefaultAcl`, `removeAcl`, `setAcl`, and `getAclStatus`, all using `AclEntry` lists or `AclStatus`.
- Extended attribute APIs include `setXAttr` with and without `EnumSet<XAttrSetFlag>`, `getXAttr`, `getXAttrs` for all or selected names, `listXAttrs`, and `removeXAttr`.
- Snapshot APIs include default and named `createSnapshot`, `renameSnapshot`, and `deleteSnapshot`.
- Storage policy APIs include `setStoragePolicy`, `unsetStoragePolicy`, `getStoragePolicy`, and `getAllStoragePolicies`.
- Static/default fields exposed in this chunk include `LOG`, `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, and `SHUTDOWN_HOOK_PRIORITY`.

### `FileStatus`

- `FileStatus` implements `Writable` and `Comparable` and represents client-side file metadata.
- Constructors cover an empty writable instance, basic length/directory/replication/block-size/modification-time/path status, status with access time/permission/owner/group, status with symlink path, and a copy constructor that can throw `IOException`.
- Accessors expose file length, file/directory/symlink classification, block size, replication, modification and access timestamps, `FsPermission`, encryption status, owner, group, path, and symlink target.
- Mutators allow path, permission, owner, group, and symlink assignment.
- Persistence and identity methods include `write(DataOutput)`, `readFields(DataInput)`, `compareTo`, `equals`, `hashCode`, and `toString`.
- `isDir()` is retained as a deprecated old-style classifier in favor of explicit `isFile()` and `isDirectory()`.

### `FileSystem`

- `FileSystem` is the abstract base class for Hadoop filesystem implementations. It extends `Configured` and implements `Closeable`.
- Construction and lookup APIs include static `get` overloads, `newInstance` overloads, local filesystem lookup, default URI get/set helpers, filesystem class lookup, per-UGI close, and global close of cached filesystems.
- URI and identity APIs include `initialize`, `getScheme`, abstract `getUri`, `getCanonicalUri`, `canonicalizeUri`, `getDefaultPort`, `getFSofPath`, `getCanonicalServiceName`, deprecated `getName`, deprecated `getNamed`, `makeQualified`, and `checkPath`.
- Security integration is visible through `addDelegationTokens(String renewer, Credentials credentials)`, which obtains tokens not already present in credentials.
- File creation/opening APIs include many `create` overloads with overwrite, buffer size, replication, block size, progress callback, checksum options, permissions, and create flags; `primitiveCreate`; `primitiveMkdir`; `createNonRecursive`; `createNewFile`; `append`; and `concat`.
- Metadata and namespace operations include `open`, `truncate`, `setReplication`, old boolean `rename`, exception-rich `rename` with `Options.Rename[]`, `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, deprecated `getLength`, `getContentSummary`, and `getQuotaUsage`.
- Listing/globbing APIs include `listStatus` overloads, `listCorruptFileBlocks`, `globStatus` overloads with optional `PathFilter`, `listLocatedStatus` overloads, `listStatusIterator`, and recursive `listFiles`.
- Working-directory and local-copy APIs include `getHomeDirectory`, `setWorkingDirectory`, `getWorkingDirectory`, `getInitialWorkingDirectory`, `mkdirs`, copy/move from local, copy/move to local, `startLocalOutput`, and `completeLocalOutput`.
- Capacity/default APIs include `getUsed`, path-scoped `getUsed`, deprecated `getBlockSize`, `getDefaultBlockSize`, path-scoped default block size, default replication, path-scoped default replication, and `getServerDefaults`.
- Symlink and checksum APIs include `createSymlink`, `getFileLinkStatus`, `supportsSymlinks`, `getLinkTarget`, `resolveLink`, `getFileChecksum` overloads, `setVerifyChecksum`, and `setWriteChecksum`.
- Administrative metadata APIs include `getStatus`, `setPermission`, `setOwner`, `setTimes`, snapshots, ACLs, xattrs, storage policies, trash roots, statistics, symlink global enablement, per-instance `StorageStatistics`, and global storage statistics.
- Fields include configuration keys/defaults (`FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`), `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, and per-filesystem `statistics`.

### `FileUtil`

- `FileUtil` is a static utility collection for file-processing tasks across Hadoop filesystems and local disk.
- Conversion helpers map `FileStatus[]` to `Path[]`.
- Deletion helpers include `fullyDelete`, `fullyDeleteContents`, and recursive delete variants with symlink-aware behavior.
- Copy helpers move data between `FileSystem` instances, from local disk to a filesystem, from a filesystem to local disk, and merge source files through `copyMerge`.
- Local path helpers include `makeShellPath` overloads, `readLink`, disk usage calculation through `getDU`, archive extraction through `unZip` and `unTar`, and temporary file creation.
- Permission and ownership helpers wrap platform-sensitive operations: `symLink`, `chmod`, recursive `chmod`, `setOwner`, readable/writable/executable setters and testers, and `setPermission`.
- Miscellaneous helpers include atomic-ish `replaceFile`, safe wrappers around `File.listFiles()` and `File.list()`, classpath-jar generation through `createJarWithClassPath`, and filesystem URI comparison through `compareFs`.
- `SYMLINK_NO_PRIVILEGE` is exposed as a return/status code for symlink creation failures caused by missing privilege.

### `FilterFileSystem`

- `FilterFileSystem` extends `FileSystem` and wraps another `FileSystem` held in the protected `fs` field. `swapScheme` is also exposed.
- Constructors support an empty instance and a wrapper around an existing raw filesystem.
- `getRawFileSystem()` exposes the wrapped target.
- Most methods delegate to the wrapped filesystem while preserving the `FileSystem` public contract: initialization, URI/canonical URI, path qualification/checking, block locations, path resolution, open/create/append/concat, listing, delete, rename, truncate, working directory, copy helpers, capacity/defaults, status, access checks, symlinks, checksums, configuration, close, ownership/times/permissions, primitive create/mkdir, child filesystems, snapshots, ACLs, xattrs, storage policies, and trash roots.

### Constants and stream/base types

- `FsConstants` exposes public filesystem constants: `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`.
- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`. It wraps an input stream with Hadoop seek/positioned-read APIs, byte-buffer reads, enhanced buffer-pool reads, file descriptor access, readahead/drop-behind controls, buffer release, unbuffering, and `toString`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable` and `CanSetDropBehind`. Constructors can bind a raw output stream, filesystem statistics, and an initial start position. Methods expose current position, close, legacy `sync`, `hflush`, `hsync`, and drop-behind control.
- `FSError` extends `Error` for unexpected filesystem errors presumed to reflect native disk failures.
- `FSInputStream` is an abstract `InputStream` implementing `Seekable` and `PositionedReadable`. Subclasses must implement `seek`, `getPos`, and `seekToNewSource`; the base class supplies positioned `read`, argument validation, and `readFully` overloads.
- `FsServerDefaults` implements `Writable` and carries server-provided defaults: block size, bytes per checksum, write packet size, replication, file buffer size, encrypted data transfer flag, trash interval, and checksum type.

## Control Flow and State

The file and namespace APIs follow Hadoop's layered filesystem control flow. `FileContext` is a path-oriented client facade that resolves links, locates the target filesystem, and exposes exception-rich operations. `FileSystem` is the implementation base class behind those calls, with static factory/cache methods selecting concrete filesystems by URI scheme and authority, then instance methods executing file creation, reads, writes, listing, metadata mutation, and admin operations.

Create/write flows generally return `FSDataOutputStream`; read flows return `FSDataInputStream`. `FSDataInputStream` delegates seeks and positioned reads to `FSInputStream`-style capabilities where available, while enhanced byte-buffer APIs add buffer-pool lifecycle through `read(ByteBufferPool, int, EnumSet)` and `releaseBuffer`.

`FilterFileSystem` inserts a delegation layer. It preserves the `FileSystem` API while routing operations to an underlying raw filesystem, which is how Hadoop can wrap implementations for checksumming, filtering, scheme adaptation, or compatibility behavior.

Delete-on-exit state is process-local. `FileSystem.deleteOnExit` marks paths for deletion when the filesystem closes, while `FileContext.deleteOnExit` marks paths for JVM shutdown. The chunk also exposes shutdown hook priority fields for both classes.

Statistics are global and per-filesystem. `FileContext` and `FileSystem` include methods to get, clear, print, and enumerate `FileSystem.Statistics`; `FileSystem` additionally exposes `StorageStatistics` and global storage statistics.

## Persistence and Serialization

`FileStatus` and `FsServerDefaults` implement `Writable`, so the empty constructors and `write`/`readFields` APIs are part of Hadoop's binary serialization contract. `FileStatus` persists metadata such as path, length, directory/file/link state, replication, block size, times, permissions, owner, group, symlink target, and encryption status. `FsServerDefaults` persists client defaults learned from a server.

Streams and filesystem instances manage runtime state rather than durable persistence. `FSDataInputStream` tracks/read delegates current input position, buffering, readahead/drop-behind preferences, and enhanced byte buffers. `FSDataOutputStream` tracks output position and sync/flush behavior. `FileSystem` instances hold configuration, URI identity, working directory state, cached instance lifecycle, delete-on-exit registrations, and statistics.

## Dependencies and Integration Points

- Core dependencies are `Path`, `FileStatus`, `BlockLocation`, `LocatedFileStatus`, `RemoteIterator`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FsServerDefaults`, `FileChecksum`, `BlockStoragePolicySpi`, and `Options` types.
- Security and identity integration appears through `UserGroupInformation` close behavior, delegation tokens, `Credentials`, `AccessControlException`, owners/groups, and permission objects.
- ACL and xattr integration uses `org.apache.hadoop.fs.permission.AclEntry`, `AclStatus`, `FsAction`, `FsPermission`, `XAttrSetFlag`, and Java collections/maps.
- Stream integration uses Java IO (`InputStream`, `OutputStream`, `DataInputStream`, `DataOutputStream`, `FileDescriptor`, `DataInput`, `DataOutput`) plus Hadoop capability interfaces such as `Seekable`, `PositionedReadable`, `Syncable`, `ByteBufferReadable`, `HasEnhancedByteBufferAccess`, and `CanUnbuffer`.
- `FileUtil` integrates local `java.io.File`, shell/path conversion, archive extraction, local permissions, symlink support, and classpath manifest generation.
- Checksumming/defaults integrate with `org.apache.hadoop.util.DataChecksum.Type`, checksum options, checksum verification/write flags, and server default negotiation.

## Risks and Edge Cases

- This is generated API metadata. It should be treated as public-contract evidence, not proof of implementation behavior. Compatibility consumers should compare it with compiled classes or source when discrepancies matter.
- Rename and truncate semantics vary by filesystem. The docs explicitly warn that rename atomicity depends on the implementation, while truncate can return `false` when background block-length recovery is still in progress.
- Symlink APIs are conditional. Some filesystems do not support symlinks, global symlink enablement exists, `MAX_PATH_LINKS` constrains traversal, and `getFileStatus` versus `getFileLinkStatus` differ in whether the final symlink is followed.
- Delete-on-exit registrations are process state and can leak cleanup work or delete unexpected paths if reused `FileSystem`/`FileContext` instances cross ownership boundaries.
- `FileStatus` equality, ordering, and serialization are compatibility-sensitive because clients often cache or compare statuses by path.
- ACL, xattr, snapshot, and storage-policy methods are optional or backend-dependent. Callers must expect `UnsupportedOperationException`, `IOException`, `AccessControlException`, and missing-file errors depending on filesystem implementation.
- `FilterFileSystem` wrappers can accidentally expose the raw filesystem or mis-handle URI scheme/canonicalization if `swapScheme` and delegation are inconsistent.
- `FileUtil` performs local destructive operations and shell/permission work. Recursive delete, archive extraction, symlink creation, and chmod/chown behavior are especially platform-sensitive.
- Enhanced byte-buffer reads require callers to release buffers correctly; failing to do so can leak pooled or off-heap buffers.

## Test Signals

- API compatibility tests should verify every public class/interface, constructor, method, field, implemented interface, return type, parameter type, checked exception, visibility, and deprecation state represented in this chunk.
- `FileSystem` tests should cover URI-based factory lookup and caching, default URI configuration, canonical URI/default port behavior, path qualification/checking, local filesystem lookup, `newInstance` cache bypass, `closeAll`, and `closeAllForUGI`.
- File operation tests should cover open/create overloads, non-recursive create, append optional behavior, concat, create-new-file existence races, replication changes, rename overwrite rules, truncate synchronous/asynchronous return values, recursive delete, delete-on-exit/cancel/process behavior, and content/quota summaries.
- Listing tests should cover files versus directories, path filters, glob patterns, corrupt-file iterators, located-status iterators, lazy `RemoteIterator` behavior, and recursive `listFiles`.
- Metadata tests should cover permissions, owner/group, times, checksums with length-limited checksum calls, checksum verify/write flags, ACL replacement/incremental removal, xattr set/get/list/remove, snapshots, storage policies, trash roots, and symlink resolution/link-status distinctions.
- Serialization tests should round-trip `FileStatus` and `FsServerDefaults`, including symlink and non-symlink constructors, permissions, owner/group, access/modification times, replication, block size, encryption flag, and checksum type.
- Stream tests should cover seek/getPos, positioned read not changing stream position, `readFully` EOF behavior, `seekToNewSource`, byte-buffer reads, enhanced buffer release, file descriptor access, readahead/drop-behind unsupported cases, output `getPos`, `hflush`, `hsync`, legacy `sync`, close semantics, and statistics updates.
- `FilterFileSystem` tests should assert delegation to the wrapped filesystem for representative operations and verify URI/scheme/path behavior remains consistent.
- `FileUtil` tests should cover recursive deletion with symlinks, copy/copyMerge across local and Hadoop filesystems, shell path conversion, archive extraction, symlink/chmod/chown return behavior, permission setters/testers, temp-file creation, replacement behavior, safe list wrappers on null-returning directories, classpath jar manifest generation, and filesystem comparison.
