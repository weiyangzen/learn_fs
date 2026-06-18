# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.10.2.xml lines 6159-12105

## Scope

This chunk is a JDiff API-description slice for Hadoop Common 2.10.2. It begins at the tail of `org.apache.hadoop.fs.CreateFlag`, covers complete public API entries for `FileAlreadyExistsException`, `FileChecksum`, `FileContext`, `FileStatus`, `FileSystem`, and `FileUtil`, and ends inside the early method list for `FilterFileSystem`. Because the source is generated XML API metadata rather than implementation code, control-flow and persistence notes are inferred from method contracts, exception surfaces, abstract/default method status, and documented delegation patterns.

The covered API surface is the core Hadoop filesystem contract: client path resolution, file and directory creation, open/read/write streams, metadata/status objects, symlinks, ACLs, xattrs, snapshots, storage policies, filesystem statistics, utility copying/deletion helpers, and filter/decorator filesystem delegation.

## Purpose

The chunk documents Hadoop's stable `org.apache.hadoop.fs` client interface. `FileContext` is presented as the newer context-oriented API that carries default filesystem, working directory, user identity, and umask while delegating operations to `AbstractFileSystem`. `FileSystem` is the older abstract base class used by HDFS, local filesystems, object stores, and third-party implementations; it defines the broad filesystem contract that user code and implementations must preserve.

The API slice also defines transfer/status support types. `FileStatus` is the writable, comparable client-side metadata record for path type, size, replication, block size, timestamps, permissions, owner/group, encryption flag, and symlink target. `FileChecksum` is the writable abstraction for file checksums. `FileAlreadyExistsException` standardizes the create/rename failure for existing targets. `FileUtil` collects local and cross-filesystem helpers for recursive delete, copy, archive extraction, permission/ownership changes, symlink creation, classpath jar expansion, and filesystem comparison. `FilterFileSystem` starts the decorator implementation that forwards `FileSystem` calls to an underlying raw filesystem.

## Important APIs, Types, and Functions

- `CreateFlag` validation appears at the chunk boundary: invalid flag combinations include `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE`, and the preceding text describes append/create semantics around complete or partial blocks.
- `FileAlreadyExistsException` extends `IOException` and is thrown when an operation targets an existing path without overwrite semantics.
- `FileChecksum` implements `Writable` and exposes `getAlgorithmName()`, `getLength()`, `getBytes()`, `getChecksumOpt()`, `equals()`, and `hashCode()`. Equality is documented in terms of both algorithm and checksum bytes.
- `FileContext` factory methods include default-config, URI-specific, local-filesystem, configuration-specific, and `AbstractFileSystem`-specific constructors through static `getFileContext()` and `getLocalFSFileContext()` variants. It exposes `getFSofPath()`, `getUgi()`, `getUMask()`, `setUMask()`, `getWorkingDirectory()`, and `setWorkingDirectory()`.
- `FileContext` path/data operations include `makeQualified()`, `resolvePath()`, `create()`, `mkdir()`, `delete()`, `open()`, `truncate()`, `setReplication()`, `rename()`, permission/owner/time setters, checksums, link status/target, `msync()`, listing, corrupt-block and located-status iterators, `deleteOnExit()`, and `util()`.
- `FileContext` metadata feature methods include ACL modification/removal/replacement/query, xattr set/get/list/remove, snapshot create/rename/delete, and storage policy set/unset/get/list. The API consistently reports access, existence, parent-directory, unsupported-filesystem, RPC, and invalid-path failures.
- `FileContext` constants and fields include `DEFAULT_PERM`, `DIR_DEFAULT_PERM`, `FILE_DEFAULT_PERM`, `SHUTDOWN_HOOK_PRIORITY`, and an SLF4J `LOG`; the doc explicitly keeps `DEFAULT_PERM` for compatibility after HADOOP-9155 split file and directory defaults.
- `FileStatus` implements `Writable` and `Comparable<FileStatus>` with constructors for non-symlink and symlink-aware filesystems plus a copy constructor. Methods expose length, file/directory/symlink type, block size, replication, modification/access times, permission, encryption state, owner, group, path, symlink, serialization, comparison, equality, hashing, and string conversion. `isDir()` is deprecated in favor of `isFile()`, `isDirectory()`, and `isSymlink()`.
- `FileSystem` static entry points include `get()`, `newInstance()`, `newInstanceLocal()`, `getLocal()`, default URI getters/setters, `getFSofPath()`, `getNamed()`, `getFileSystemClass()`, `closeAll()`, `closeAllForUGI()`, global statistics accessors, symlink enablement, and global storage statistics.
- `FileSystem` abstract or implementation-critical instance APIs include `initialize()`, `getUri()`, `open()`, core `create()` overloads, `append()`, `rename()`, `delete(Path, boolean)`, `listStatus(Path)`, `getFileStatus()`, `mkdirs()`, working-directory accessors, and `getHomeDirectory()`. Many convenience overloads delegate to these core methods using configuration defaults.
- `FileSystem` optional/default operations include concat, truncate, corrupt-block listing, located listing, recursive file listing, snapshots, ACLs, xattrs, symlinks, storage policies, checksum verification/write toggles, trash root discovery, `msync()`, and builder APIs `createFile()` and `appendFile()`.
- `FileSystem` fields include `FS_DEFAULT_NAME_KEY`, `DEFAULT_FS`, public Commons Logging `LOG`, `SHUTDOWN_HOOK_PRIORITY`, `TRASH_PREFIX`, `USER_HOME_PREFIX`, and protected per-instance `statistics`.
- `FileUtil` exposes conversion helpers (`stat2Paths()`), local recursive deletion helpers (`fullyDelete*()`), cross-filesystem and local-to-filesystem copy variants, `copyMerge()`, shell path conversion, local disk usage, `unZip()`, `unTar()`, local symlink creation, `chmod()`, `setOwner()`, portable readability/writability/executability helpers, permission setting, temporary file creation, file replacement, local listing, manifest jar creation, jar directory expansion, `compareFs()`, and `SYMLINK_NO_PRIVILEGE`.
- `FilterFileSystem` in this slice wraps another `FileSystem` and begins forwarding URI, canonical URI, path validation/qualification, block location, path resolution, open, append, concat, create, list-located, create-non-recursive, replication, rename, truncate, delete, status/listing, home/working directory, status, mkdir, and local copy/output methods to the raw filesystem.

## Control Flow

`FileContext` control flow is context-first. Callers construct a context from a default configuration, URI, local filesystem constant, supplied configuration, or explicit `AbstractFileSystem`. Paths are then resolved against the context's default filesystem and working directory: fully qualified URIs keep their scheme/authority, slash-relative names use the default filesystem, and working-directory-relative names are prefixed with the context working directory. `setWorkingDirectory()` deliberately stores path text rather than following symlinks, which makes `getWorkingDirectory()` return what was set and avoids Unix inode-style process state in a multi-root distributed namespace.

Most `FileContext` operations follow a path-normalization and filesystem-dispatch pattern. A path is qualified or resolved, `getFSofPath()` selects an `AbstractFileSystem`, and the operation is invoked with the caller's context state such as umask, create flags, and create options. Create and mkdir apply the umask before delegation. Optional server-side defaults such as buffer size, block size, replication, checksum parameters, home directory, and encryption-transfer setting are supplied by the target filesystem rather than by the `FileContext` configuration layer.

`FileSystem` control flow is older and more implementation-centered. Static `get()` and `newInstance()` resolve a scheme/default URI, consult configuration and service-loaded implementations, initialize the filesystem with a URI and `Configuration`, and either return cached instances or new instances. Subclasses must forward `initialize()` to the superclass. Convenience overloads for create/open/append/mkdir/list/copy use configuration defaults and eventually call abstract or core methods implemented by concrete filesystems.

The `FileSystem` create path has many overloads converging on the permission-aware create methods and the newer `EnumSet<CreateFlag>`/`ChecksumOpt` form. `primitiveCreate()` and `primitiveMkdir()` exist to support `FileContext` during the transition from `FileSystem` by accepting already-umasked absolute permissions. `createNewFile()` is explicitly documented as non-atomic in the default implementation, so implementations or callers that require atomic existence checks need filesystem-specific support.

Rename, truncate, delete, symlink, ACL, xattr, snapshot, and storage-policy operations expose a common pattern: default methods often throw `UnsupportedOperationException` or provide weak fallback behavior, while HDFS or other capable filesystems override them. The protected `rename(Path, Path, Options.Rename...)` contract is more detailed than the boolean `rename()`, but its own documentation says the default implementation is non-atomic and temporary for `FileContext` transition.

Listing APIs split eager and lazy flows. `listStatus()` returns arrays and can be filtered or applied across path arrays. `globStatus()` expands patterns and returns sorted matches with different null/empty semantics depending on whether a glob existed. `listLocatedStatus()` and `listStatusIterator()` return `RemoteIterator` so implementations can fetch entries on demand, with located listings including block locations for files. `listFiles()` recursively lists files, optionally under a directory tree.

`deleteOnExit()` records paths for later deletion. `close()` processes queued delete-on-exit paths, releases locks, removes cached instances, and leaves further use of the filesystem or its streams undefined. Static `closeAll()` and `closeAllForUGI()` close cached filesystems globally or by user identity. `processDeleteOnExit()` is documented as `O(paths)` plus actual filesystem existence/delete cost.

`FileUtil` flows are helper pipelines rather than persistent services. Copy helpers open streams across local files and `FileSystem` instances, optionally delete sources, and optionally overwrite. Recursive delete helpers distinguish local symlinks from real directories, deleting symlink entries rather than targets for `fullyDelete()` while `fullyDeleteContents()` follows a symlink to a directory and deletes the target directory contents. Archive extraction writes zip/tar contents into target local directories. Jar creation expands classpath wildcard entries and writes a temporary manifest jar.

`FilterFileSystem` control flow is straightforward delegation. The wrapper stores or initializes a raw filesystem, exposes it through `getRawFileSystem()`, mirrors URI/canonicalization/path checks, and forwards filesystem operations. The design lets subclasses intercept selected operations while inheriting delegation for the rest.

## State and Persistence Behavior

The XML itself is generated API metadata used by compatibility/reporting tooling, so it does not persist runtime state. The documented runtime APIs, however, define several stateful contracts.

`FileContext` state is per-context: default filesystem, working directory, user/group identity through `UserGroupInformation`, and umask. This is intentionally compared to Unix per-process file namespace state, but the documentation limits configuration-derived values to default filesystem and umask; other defaults are server-side filesystem properties. Working directory changes affect future relative path resolution only and are not persisted as remote filesystem metadata.

`FileSystem` has both per-instance and global state. Per-instance state includes configuration, URI/canonical URI, working directory, delete-on-exit queue, and protected `statistics`. Global state includes cached filesystem instances, global storage statistics, old static statistics maps, symlink enabled state, default filesystem configuration keys, and shutdown hook behavior. Closing a filesystem processes delete-on-exit paths and removes the instance from the cache if cached.

`FileStatus` is a serializable metadata snapshot. It carries remote path metadata, not an open handle, and its equality/hash/compare contracts are path-name based. Writable serialization means instances are persisted/transferred through Hadoop RPC, sequence files, or other writable-based channels by implementations and clients.

Filesystem operations can mutate durable storage according to the selected implementation: create/append/truncate/concat/write streams change file data; mkdir/delete/rename/symlink/snapshot operations change namespace state; permission/owner/time/ACL/xattr/storage-policy calls update metadata; checksum and status calls are read-oriented unless the concrete filesystem performs maintenance. The API makes clear that support and atomicity vary by implementation, with HDFS treated as the de facto normative behavior when documentation and implementation conflict.

`FileUtil` mutates local files, target filesystems, permissions, ownership, temporary classpath jars, and archives. It also may register JVM delete-on-exit hooks for local recursive deletion. Its methods can leave partial state: recursive local deletes and copies return false or throw after partial deletion/copy, and delete-on-exit depends on clean JVM shutdown.

## Dependencies and Integration Points

The chunk sits at the center of Hadoop Common filesystem integration. It depends on `org.apache.hadoop.conf.Configuration`, `Path`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FSDataOutputStreamBuilder`, `Options.CreateOpts`, `Options.ChecksumOpt`, `Options.Rename`, `CreateFlag`, `PathFilter`, `RemoteIterator`, `BlockLocation`, `LocatedFileStatus`, `ContentSummary`, `QuotaUsage`, `FsStatus`, `FsServerDefaults`, `BlockStoragePolicySpi`, `StorageStatistics`, and `GlobalStorageStatistics`.

Security and identity integration appears through `UserGroupInformation`, delegation token APIs, canonical service names, `SecurityUtil`, access-control exceptions, ACL types, xattr permission filtering, and UGI-scoped cache closing. Permission integration uses `FsPermission` and ACL status/entry types. RPC-specific exceptions are called out in many `FileContext` contracts, including client/server/unexpected server exceptions.

Implementation discovery integrates with configuration bindings and Java `ServiceLoader` through `getFileSystemClass()`. URI behavior integrates `java.net.URI`, default ports, canonical hostname/port normalization, and path scheme/authority validation. `FileSystem` docs name local filesystems, HDFS `DistributedFileSystem`, object stores, and external third-party filesystems as implementations of this contract.

Local/platform integration is concentrated in `FileUtil`: `java.io.File`, local delete-on-exit, shell-path conversion, archive extraction, chmod/chown-like operations, portable permission checks, Windows-specific symlink privilege behavior, and manifest jar/classpath handling. `FilterFileSystem` is an integration layer for wrappers such as checksum, view, or instrumentation filesystems that need to expose the same API while delegating to another filesystem.

## Risks and Edge Cases

Path qualification semantics are a major compatibility risk. Fully qualified, slash-relative, and working-directory-relative names are resolved differently, and relative paths with schemes are explicitly illegal. `FileContext.setWorkingDirectory()` does not follow symlinks; code assuming Unix current-directory inode semantics can resolve later paths differently from expectation.

Create semantics combine flags, umask, permissions, parent creation, server-side defaults, and optional checksum settings. Invalid `CreateFlag` combinations must be rejected consistently, and create-parent defaults differ from recursive convenience methods. `createNewFile()` is not atomic by default, which is dangerous for lock-file or single-writer protocols on filesystems that do not override it.

Rename and truncate semantics are not uniformly strong. The protected rename-with-options contract defines overwrite rules and failure modes, but documents default non-atomic behavior. Truncate may return `false` to indicate asynchronous last-block recovery before subsequent append/write operations can safely proceed.

Delete-on-exit is expensive and unreliable for remote filesystems. It requires the path to exist when scheduled, depends on clean JVM shutdown or explicit `close()`, can significantly delay shutdown on object stores or remote filesystems, and can fail under connectivity problems.

Default/optional operations can mask unsupported capabilities. Many methods have default no-op, null, true, or `UnsupportedOperationException` behavior: checksum retrieval may return null; `setReplication()` may return true even when unsupported; checksum toggles may do nothing; ACL/xattr/snapshot/storage-policy methods may be unsupported. Tests and callers need to distinguish "unsupported but accepted" from "changed durable state."

`FileStatus` equality is path-based rather than full metadata-based. Caches or sets of status objects that expect size, permission, timestamp, encryption, or symlink differences to affect equality will miss changes. Deprecated helpers such as `isDir()`, `getReplication(Path)`, `getLength(Path)`, and block-size/default-replication no-arg methods remain for compatibility and can encourage inefficient extra `getFileStatus()` calls.

`FileUtil` recursive deletion has symlink-specific behavior that differs between deleting a symlink and deleting contents of a symlinked directory. Partial deletion/copy is explicitly possible. Shell, chmod, ownership, symlink, and permission helpers are platform-sensitive, especially on Windows where symlink privilege and folder execute-bit behavior differ from Unix.

Statistics APIs are split between deprecated static `Statistics` maps and newer `StorageStatistics`/`GlobalStorageStatistics`. Implementations that only update one path can create misleading metrics. Static statistics methods are synchronized; high-frequency global metric access can become a contention point.

`FilterFileSystem` wrappers can accidentally bypass wrapper policy if new `FileSystem` APIs are not overridden and are inherited as direct delegation. This is especially relevant for security checks, xattrs/ACLs/storage policies, checksums, builder APIs, and path canonicalization.

## Test Signals

Useful validation for this API surface should focus on cross-implementation contract behavior:

- `FileContext` path resolution for fully qualified, slash-relative, working-directory-relative, and illegal scheme-relative paths, including working directories in a different filesystem from the default.
- `FileContext` create and mkdir with umask application, explicit permissions, create-parent true/false, server-side buffer/block/replication/checksum defaults, and invalid `CreateFlag` combinations.
- `FileSystem.get()`/`newInstance()` resolution through default URI, explicit URI, service-loaded schemes, cached vs uncached instances, UGI-specific access, `closeAllForUGI()`, and unsupported schemes.
- Core create/open/append/rename/delete/truncate behavior on local FS, HDFS-compatible FS, and object-store implementations, especially overwrite handling, non-recursive create parent failures, rename option semantics, and truncate's `false` asynchronous result.
- `deleteOnExit()` and `close()` behavior for cached and uncached filesystems, missing paths at close time, large delete queues, remote failure injection, and cache removal after close.
- Listing behavior for `listStatus`, path filters, path-array listing, glob null-vs-empty semantics, sorted glob results, `listLocatedStatus`, `listStatusIterator`, and recursive `listFiles()`.
- `FileStatus` writable round trips, copy constructor, symlink target handling, encrypted flag, default permission/owner/group fallbacks, path-based `equals()`/`hashCode()`, and deprecated `isDir()` compatibility.
- Checksum behavior for filesystems with and without checksum support, including `getFileChecksum(path, length)`, `FileChecksum.equals()`, and `setVerifyChecksum()`/`setWriteChecksum()` no-op behavior on unsupported filesystems.
- ACL, xattr, snapshot, storage-policy, trash-root, and `msync()` calls on supporting and non-supporting filesystems, verifying both successful durable changes and correct `UnsupportedOperationException`/`IOException` surfaces.
- Statistics tests covering per-instance `getStorageStatistics()`, global storage statistics, deprecated synchronized statistics methods, `clearStatistics()`, and wrapper filesystems.
- `FileUtil` tests for local recursive delete with files, directories, symlinks to files, symlinks to directories, permission-grant retries, partial failure; copy/copyMerge across local/HDFS-like filesystems with overwrite/deleteSource; archive extraction; shell-path conversion; chmod/setOwner; Windows symlink privilege return code; jar wildcard expansion; and `compareFs()`.
- `FilterFileSystem` delegation tests verifying every forwarded method reaches the raw filesystem with the expected path/arguments, and wrapper-specific policy remains effective for path checks, create/open/delete, status/listing, local copy, canonical URI, and optional features.

## Cross-Chunk Notes

This chunk continues from the earlier `CreateFlag` definition and stops before the full `FilterFileSystem` API entry is complete. The merge lane should combine this document with adjacent chunks for the rest of `FilterFileSystem` and nearby `org.apache.hadoop.fs` types. For this source file, remember that the JDiff XML records public API shape and documentation rather than executable implementation; final research should separate API compatibility guarantees from behavior that must be confirmed in the corresponding Java sources.
