# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 5867-11840

## Scope

This chunk covers a JDiff XML API report for part of the Hadoop Common 2.6.0 public/protected Java API. It starts at the tail of `org.apache.hadoop.fs.CommonConfigurationKeysPublic`, then covers file-system-facing types from `ContentSummary` through most of `FileUtil`. The largest API surfaces in this range are `FileContext`, `FileSystem`, `FileStatus`, `FileSystem.Statistics`, and local/file-system utility helpers.

The source is not implementation code. It records class names, method signatures, visibility, deprecation state, thrown exceptions, field declarations, implemented interfaces, and embedded Javadoc. Research therefore treats this chunk as an API contract and compatibility surface for Hadoop filesystem clients and filesystem implementations.

## Purpose

The chunk describes Hadoop Common filesystem APIs used by applications, shells, MapReduce/YARN components, HDFS clients, local filesystem adapters, token management code, and tests. It defines how callers discover filesystems, qualify paths, create/open/append files, list directories, inspect metadata, manipulate permissions/owners/timestamps, handle symlinks, manage ACLs and xattrs, obtain delegation tokens, copy data across local and distributed filesystems, and collect per-filesystem IO statistics.

It also preserves compatibility details for older API entry points. Several methods are deprecated in favor of newer path-aware or `FileContext`-oriented calls, but remain part of the Hadoop 2.6 public surface. The JDiff report is used to detect API drift across Hadoop releases, so method overloads and deprecation metadata are themselves important output.

## Important APIs, Types, and Data

The chunk begins with final public configuration constants for KMS encrypted-key cache behavior and secure-random settings in `CommonConfigurationKeysPublic`. These include cache low-watermark, refill-thread, expiry, Java secure-random algorithm, secure-random implementation, and device-file-path keys/defaults. They bind client-side crypto/token behavior to `core-default.xml` configuration names.

`ContentSummary` is a `Writable` record for directory/file aggregate state. Its constructors cover empty, basic length/file/directory counts, and quota-aware length/count/space forms. Accessors expose content length, directory count, file count, namespace quota, disk space consumed, and space quota. `write` and `readFields` make the object serializable through Hadoop IO, while `getHeader` and overloaded `toString` methods format quota-aware and human-readable command output.

`CreateFlag` is an enum contract for file creation semantics. `CREATE`, `APPEND`, `OVERWRITE`, and `SYNC_BLOCK` can be combined by callers, then validated with overloads of `validate`. The Javadoc specifies valid combinations such as create-only, append-only, overwrite-only, create-or-append, and create-or-overwrite. `APPEND|OVERWRITE` and `CREATE|APPEND|OVERWRITE` are invalid and should throw `HadoopIllegalArgumentException`; path-aware validation also maps existence checks to `FileAlreadyExistsException` or `FileNotFoundException` behavior.

`DelegationTokenRenewer.Renewable` and `DelegationTokenRenewer.RenewAction` define the renewal hook used by filesystems that need automatic delegation-token replacement. `Renewable` supplies `getRenewToken` and `setDelegationToken`. `RenewAction` implements `Delayed` with validity, delay, ordering, equality, hash, and string methods so renewals can be scheduled in a delay queue.

`DUHelper` exposes disk-usage helper entry points: `getFolderUsage`, instance `check`, `getFileCount`, `getUsage`, and a `main` entry point. `FileAlreadyExistsException` is an `IOException` subclass used when a target already exists and overwrite was not requested. `FileChecksum` is an abstract `Writable` with algorithm name, byte length, raw checksum bytes, `Options.ChecksumOpt`, and equality/hash semantics based on algorithm and value.

`FileContext` is a higher-level namespace context around `AbstractFileSystem`. It has factory overloads for default configuration, explicit `Configuration`, explicit URI, explicit default `AbstractFileSystem`, and local filesystem contexts. It maintains path resolution state such as default filesystem, user/group identity, working directory, and umask. Its constants distinguish legacy default permissions from `DIR_DEFAULT_PERM` and `FILE_DEFAULT_PERM`, and it has a shutdown-hook priority for delete-on-exit cleanup.

`FileContext` operations cover create, mkdir, delete, open, set replication, rename, permission/owner/time changes, checksums, file status, access checks, symlink creation and target inspection, block locations, filesystem capacity/status, listing, corrupt-block listing, located listing, delete-on-exit, path resolution, filesystem statistics, delegation tokens, ACL operations, and xattr operations. The embedded symlink documentation is unusually detailed: final-component symlinks are handled differently by delete, rename, link-status, and target APIs than by APIs that follow links; targets may be fully qualified URIs, partially qualified URIs, relative paths, or absolute paths.

`FileContext.Util` is a convenience facade for common derived operations. It provides existence checks, content summaries, list-status overloads with filters and varargs, recursive file listing, globbing, and copy helpers from `Path` to `Path` or into an output stream. These utilities sit above the primitive `FileContext` operations and are important for callers that want arrays or iterators rather than lower-level filesystem calls.

`FileStatus` is a `Writable` and `Comparable` metadata record. Constructors represent empty status, basic length/directory/replication/block-size/modification-time/path state, full permission/owner/group/access-time state, symlink-aware state, and copy construction. Getters expose length, file/directory status, deprecated `isDir`, symlink state and target, block size, replication, modification/access time, permissions, encryption bit, owner, group, and path. Mutators allow setting path, permission, owner, group, and symlink before serialization. Comparison/equality/hash/string methods make statuses sortable and usable in filesystem listings and glob results.

`FileSystem` is the core abstract base class for Hadoop filesystem implementations. Static discovery APIs include `get`, `newInstance`, `getLocal`, `newInstanceLocal`, `getDefaultUri`, `setDefaultUri`, `getFileSystemClass`, and cache controls such as `closeAll` and `closeAllForUGI`. Instance identity APIs include `initialize`, scheme/URI/canonical URI/default port, canonical service name for token lookup, child filesystems, path qualification, and path validation. The class has public constants for the default filesystem key/name, logging, shutdown-hook priority, and a protected `statistics` field.

`FileSystem` file operations include many `create` overloads, `primitiveCreate`, `primitiveMkdir`, deprecated `createNonRecursive` overloads, `createNewFile`, `open`, `append`, `concat`, `rename`, `delete`, `deleteOnExit`, `cancelDeleteOnExit`, `processDeleteOnExit`, `exists`, `isDirectory`, `isFile`, length/content summary lookup, list-status overloads, globbing, located status, recursive file listing, home/working directory management, mkdirs, local copy/move helpers, local output staging, close, used space, block/default block size, replication, status, and permission/owner/time mutation.

`FileSystem` also exposes symlink, checksum, snapshot, ACL, xattr, and statistics APIs. Snapshot calls create default or named snapshots, rename snapshots, and delete snapshots. ACL methods mirror `FileContext`: modify, remove entries, remove default ACL, remove all but base ACL, fully set, and retrieve status. XAttr methods set with optional flags, get one, get all, get named set, list names, and remove. Static statistics calls return or reset per-scheme/per-class statistics; symlink enablement is also exposed globally.

`FileSystem.Statistics` is a write-optimized counter object keyed by scheme. It has constructors, thread-local data access, increment methods for bytes read/written and read/large-read/write operations, aggregate getters, `reset`, `toString`, and `getScheme`. `StatisticsData` exposes the per-thread volatile counters and getters. The docs explain the design: writers update thread-local data to avoid contention, readers aggregate across thread-local areas, and reset offsets root data rather than mutating other threads' thread-local state.

`FileUtil` collects static local and cross-filesystem helpers. This chunk covers conversion from `FileStatus[]` to `Path[]`, recursive local deletion with explicit symlink semantics, symlink target reading, content-only deletion, deprecated filesystem recursive deletion, inter-filesystem and local/filesystem copy overloads, copy-merge, shell-path conversion, local disk usage, unzip/untar, local symlink creation, chmod/chown-style ownership and permission helpers, portable readable/writable/executable setters and access checks, `FsPermission` application, temp-file creation, file replacement, safe wrappers around `File.listFiles()` and `File.list()`, and the beginning of `createJarWithClassPath`.

## Control Flow

Most control flow is implicit in API layering. `FileContext` resolves a caller path against its default filesystem, working directory, and symlink rules, finds the relevant `AbstractFileSystem` with `getFSofPath`, and delegates filesystem operations while preserving `FileContext` state such as umask and user identity. Relative paths are not interpreted as process-current-directory paths; they are prefixed with the `FileContext` working directory.

File creation flows normalize caller intent through `CreateFlag`, permissions, umask, replication, block size, buffer size, progress callbacks, and optional checksum options. `FileSystem` exposes numerous convenience overloads that funnel toward abstract or protected primitive methods implemented by concrete filesystems. Static `FileSystem.create(fs, path, permission)` and `mkdirs(fs, path, permission)` intentionally use follow-up permission setting to avoid process-wide configuration mutation, trading an extra RPC for thread safety.

Listing flows differ by API shape. `listStatus` returns arrays in `FileSystem` and remote iterators in `FileContext`; `listLocatedStatus` includes block locations for files; `listFiles` can recurse through a subtree and emits file statuses with block locations. Glob calls expand path patterns and return sorted statuses, with a documented distinction between no-match on non-glob paths (`null`) and no-match on glob paths (empty array).

Symlink flow is explicitly split between operations that act on a final symlink and operations that resolve it. Delete, delete-on-exit, rename, link-status, and get-link-target operate on the symlink itself for the final path component. Most open, metadata, checksum, block-location, status, and listing operations follow symlinks. Intermediate symlinks are resolved transparently, and `resolve`/`resolveIntermediate` expose protected helpers for all-symlink or intermediate-only resolution.

Delegation-token flow starts from canonical service names. A filesystem with its own token returns a unique service string and can produce a token via `getDelegationToken`; callers should prefer `addDelegationTokens`, which avoids duplicating tokens already present in `Credentials` and can recurse into child filesystems for embedded filesystems. `FileContext.getDelegationTokens` asks for all filesystems accessed for a given path.

Statistics flow is low-contention by design. IO paths increment thread-local counters through `FileSystem.Statistics`; readers aggregate totals, while reset computes a negative root offset under lock instead of trying to zero thread-local counters owned by other threads.

`FileUtil` flows are utility-level. Copy helpers bridge source and destination `FileSystem` objects or local files, optionally deleting sources and overwriting destinations. Delete helpers recursively process local files/directories but avoid following symlink directories for full deletion, while content-only deletion does follow a symlink to a directory and deletes the target directory contents. Permission helpers prefer Java primitives when possible and fall back to platform commands where needed. `createJarWithClassPath` begins a flow that creates a manifest-only classpath jar to work around command-line length limits.

## State and Persistence Behavior

`ContentSummary`, `FileStatus`, and `FileChecksum` are serializable state carriers. `ContentSummary` persists aggregate counts and quotas through `Writable`; `FileStatus` persists metadata including path, permissions, ownership, times, symlink target, and encryption indicator; concrete `FileChecksum` implementations persist algorithm and bytes.

`FileContext` holds per-context state: default filesystem, working directory, umask, and UGI. This is analogous to process filesystem state but scoped to the `FileContext` object. Delete-on-exit registration persists until JVM shutdown or successful cleanup via the shutdown hook.

`FileSystem` instances are cached by URI/scheme/authority and user unless callers use `newInstance` APIs, which always create unique instances. Static cache close methods can close all cached filesystems or all cached filesystems for a specific `UserGroupInformation`. `FileSystem` also carries protected per-instance statistics and global per-scheme/per-class statistics registries.

Filesystem operations persist remote or local namespace mutations: create/append/concat/rename/delete, mkdirs, replication, permissions, owners, timestamps, symlinks, snapshots, ACLs, xattrs, and copied files. Snapshot APIs persist named point-in-time references in snapshot-capable filesystems. ACL/xattr APIs persist metadata only on filesystems that implement those features.

Delegation tokens persist in `Credentials` and in renewable filesystem state until renewed or replaced. `DelegationTokenRenewer.RenewAction` persists scheduled renewal timing in a delayed queue. Canonical service names are the stable keys used for token lookup.

`FileUtil` operations mostly mutate local filesystem state: recursive deletion, permission/ownership changes, symlink creation, archive extraction, temp-file creation, replacement, and classpath-jar creation. Some helpers bridge local state and distributed filesystems through copy and merge operations.

## Dependencies and Integration Points

This chunk depends on core Hadoop types: `Configuration`, `Path`, `PathFilter`, `RemoteIterator`, `FSDataInputStream`, `FSDataOutputStream`, `BlockLocation`, `FsStatus`, `FsServerDefaults`, `Options.ChecksumOpt`, `Options.Rename`, `CreateFlag`, `AclStatus`, `AclEntry`, `FsPermission`, `FsAction`, `UserGroupInformation`, `Credentials`, `Token`, `Progressable`, and Hadoop IO `Writable`.

`FileContext` integrates with `AbstractFileSystem` and with the newer filesystem API style that separates namespace context from concrete filesystem instances. `FileSystem` integrates with concrete implementations such as `LocalFileSystem`, HDFS `DistributedFileSystem`, embedded/composite filesystems, and service loading via `fs.<scheme>.class` configuration keys.

Security integration appears in access checks, ACLs, xattrs, delegation tokens, canonical service names, `Credentials`, `UserGroupInformation`, KMS configuration constants, and secure-random configuration constants. Access checks explicitly warn about time-of-check/time-of-use races and recommend running the actual operation as the desired user instead.

RPC integration is visible in exception documentation for remote filesystems: `RpcClientException`, `RpcServerException`, and `UnexpectedServerException` may surface from many `FileContext` operations. Block locations, replication, server defaults, checksums, snapshots, ACLs, and xattrs are especially tied to HDFS-style remote implementations.

Local platform integration is concentrated in `FileUtil`: Java `File` APIs, shell path conversion, symlink/chmod/chown behavior, Windows-specific permission and symlink limitations, archive extraction, manifest classpath jars, and wrappers that turn ambiguous `File.list*()` null returns into `IOException`.

The JDiff XML itself integrates with API compatibility tooling. Additions, removals, visibility changes, changed exceptions, or changed deprecation status in this file are signals for release compatibility review.

## Risks and Edge Cases

The biggest API risk is compatibility drift. `FileContext`, `FileSystem`, and `FileStatus` are widely consumed, and changing overloads, return types, exceptions, visibility, or deprecation state can break applications and third-party filesystem implementations even when implementation behavior remains similar.

Create flag validation is a correctness boundary. Invalid combinations such as append plus overwrite must be rejected consistently, and path-existence-aware validation must map missing/existing paths to the documented create, append, and overwrite semantics.

Symlink semantics are subtle. Full deletion of a symlink to a directory deletes only the symlink, while content-only deletion of a symlink to a directory deletes the target directory contents. FileContext final-component behavior also varies by operation. Regressions here can cause either unexpected dangling paths or destructive deletion of targets.

`FileContext.access` and `FileSystem.access` are explicitly subject to TOCTOU races. A successful access check is not a guarantee that a later operation will be allowed or will target the same object, especially on remote or concurrently modified filesystems.

`FileSystem` caching can leak resources or reuse state under the wrong user/configuration if callers choose `get` when they needed `newInstance`, or forget to close cached instances during tests. Conversely, `closeAll` and `closeAllForUGI` are dangerous if other code still relies on cached filesystems.

Permission behavior has historical traps. `FileContext.DEFAULT_PERM` used to apply to files and could give files execute bits; newer code should use `DIR_DEFAULT_PERM` or `FILE_DEFAULT_PERM`. The static `FileSystem.create` helper uses two RPCs to set exact permissions, so partial failure or race behavior differs from setting a umask globally.

Statistics reset is intentionally non-obvious. Implementations or tests that assume counters are physically zeroed per thread can misread the design; reset uses a root offset because other threads' thread-local counters cannot be safely mutated.

`FileUtil` local operations are platform-sensitive. Windows symlink creation can fail due to security policy and return a special code; Java readable/writable/executable APIs do not behave uniformly across platforms; revoking execute permission from directories differs on Windows; shell path and classpath-jar logic must account for command-line length and environment expansion.

The chunk ends before the completion of `FileUtil.createJarWithClassPath` documentation and before the `FileUtil` class close. Full analysis of that helper and subsequent nested `FileUtil.HardLink` requires the next chunk.

## Test Signals

Useful validation signals for this chunk include API compatibility checks generated from JDiff: stable class names, method overloads, parameter types, return types, thrown exceptions, field names, visibility, static/final flags, implemented interfaces, and deprecation annotations.

Filesystem behavior tests should cover `FileContext` and `FileSystem` create/open/append/rename/delete/mkdir/list/glob flows across local and HDFS-like implementations, including relative paths, slash-relative paths, fully qualified URIs, working directory changes, default filesystem resolution, and `makeQualified`.

Create semantics tests should cover every documented `CreateFlag` combination, invalid combinations, existing path, missing path, append-only, overwrite-only, create-or-append, create-or-overwrite, `SYNC_BLOCK`, non-recursive create, checksum options, replication, block size, progress callbacks, and exact permission application.

Metadata tests should cover `FileStatus` serialization/deserialization, comparison and equality, symlink targets, encrypted flags, path mutation, permission/owner/group mutation, and content summary quota and human-readable formatting.

Symlink tests should cover final symlink handling for delete, delete-on-exit, rename, get-link-target, get-file-link-status, open/status/checksum/block-location operations that follow links, dangling symlinks, fully qualified targets, partially qualified targets, relative targets, absolute targets, and intermediate symlink resolution.

Security tests should cover access checks, ACL modify/remove/default/remove-all/set/get flows, xattr set/get/list/remove flows with namespace-prefixed names, token acquisition through `addDelegationTokens`, canonical service names, child filesystem token propagation, and renewer scheduling/replacement.

Statistics tests should cover per-thread increments, aggregate reads, reset behavior under concurrent writers, scheme/class statistics lookup, `clearStatistics`, and printed statistics output.

`FileUtil` tests should cover recursive deletion of normal files, directories, symlinks to files, symlinks to directories, content-only deletion through symlink directories, copy/copyMerge local and cross-filesystem paths with delete-source and overwrite variants, archive extraction, shell-path conversion, chmod/chown/permission helpers, Windows-specific permission behavior where available, safe list wrappers converting null returns to `IOException`, temp-file creation, replace-file behavior, and classpath-jar generation on long classpaths.

## Cross-Chunk Notes

Line 5867 starts inside the final field block of `CommonConfigurationKeysPublic`; the class starts in the preceding chunk. Line 11840 stops inside the Javadoc for `FileUtil.createJarWithClassPath(String, Path, Path, Map)`, before the method documentation, `FileUtil` class, and nested `FileUtil.HardLink` entry are complete. The merge lane should combine adjacent chunks for a complete per-file report.
