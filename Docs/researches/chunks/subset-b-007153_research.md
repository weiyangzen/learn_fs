# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_2.6.0.xml lines 11841-17787

## Scope

This chunk is a JDiff API descriptor slice for Hadoop Common 2.6.0. It starts at the tail of `org.apache.hadoop.fs.FileUtil`, covers a broad portion of the `org.apache.hadoop.fs` public API surface, then continues through filesystem crypto, FTP, permission, and viewfs packages. It ends in the middle of `org.apache.hadoop.fs.viewfs.ViewFs`, so final per-file reconciliation must merge adjacent chunks before making complete claims about that class.

The descriptor is generated API metadata, not executable code. It records public/protected constructors, methods, fields, inheritance, implemented interfaces, checked exceptions, deprecation notes, and selected Javadocs consumed by API compatibility tooling.

Visible package areas include:

- `org.apache.hadoop.fs`: filesystem wrappers, stream wrappers, constants, shell permission commands, hard links, Hadoop Archives, local filesystem adapters, path and path exception types, read/sync/iterator contracts, trash policies, xattr helpers, checksum options, and create/rename option types.
- `org.apache.hadoop.fs.crypto`: encrypted `FSDataInputStream` and `FSDataOutputStream` wrappers.
- `org.apache.hadoop.fs.ftp`: FTP-backed `FileSystem` and its runtime exception wrapper.
- `org.apache.hadoop.fs.permission`: ACL entry/status builders, permission actions, permission serialization, and a deprecated filesystem access-control exception.
- `org.apache.hadoop.fs.viewfs`: viewfs configuration helpers/constants, mountpoint exception, `ViewFileSystem`, mountpoint marker type, and the beginning of `ViewFs`.

## Purpose

This XML chunk preserves Hadoop Common 2.6.0's filesystem-facing public API contract. The APIs here are the client-side substrate used by HDFS, local filesystems, archive filesystems, FTP integrations, viewfs mount tables, shell commands, path validation, permission and ACL processing, xattr encoding, stream positioning, sync semantics, and trash behavior.

At runtime in Hadoop, these types define how callers discover filesystem implementations, qualify and validate paths, read and write byte streams, propagate permissions and ACLs, move data to trash, resolve mount tables, and adapt special backends such as HAR, local disk, FTP, and encrypted streams. In this descriptor, their purpose is compatibility: downstream projects and tests can compare this release's public contract against other Hadoop releases.

## Important APIs, Types, and Functions

### Filesystem wrappers and constants

- `FileUtil.HardLink` is retained as a deprecated static class extending `org.apache.hadoop.fs.HardLink`; callers are directed to the top-level `HardLink` class.
- `FilterFileSystem` extends `FileSystem` and contains a protected `FileSystem fs` plus `swapScheme`. It forwards almost the full `FileSystem` surface to the wrapped filesystem: initialization, URI/canonical URI, path qualification/checking, block location lookup, `open`, `append`, `concat`, create variants, non-recursive create, replication, rename, delete, list operations, corrupt block iteration, located status iteration, working directory, status, mkdirs, local copy helpers, checksum toggles, owner/time/permission mutation, snapshots, ACLs, xattrs, symlinks, primitive create/mkdir, and child filesystem discovery.
- `FsConstants` exposes public constants for filesystem schemes and URIs: `LOCAL_FS_URI`, `FTP_SCHEME`, `MAX_PATH_LINKS`, `VIEWFS_URI`, and `VIEWFS_SCHEME`. `VIEWFS_URI` is documented as the client-side mount filesystem.

### Stream contracts

- `FSDataInputStream` extends `DataInputStream` and implements `Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, and `HasEnhancedByteBufferAccess`. It wraps an `FSInputStream` and provides `seek`, `getPos`, positional `read`, `readFully`, `seekToNewSource`, `getWrappedStream`, `ByteBuffer` reads, file descriptor access, readahead/drop-behind hints, enhanced byte-buffer reads with `ByteBufferPool`, and `releaseBuffer`.
- `FSDataOutputStream` extends `DataOutputStream` and implements `Syncable` and `CanSetDropBehind`. Its constructors accept an output stream, optional filesystem statistics, and optional start position. It exposes `getPos`, `close`, `getWrappedStream`, deprecated `sync`, `hflush`, `hsync`, and `setDropBehind`.
- `Seekable`, `PositionedReadable`, and `Syncable` are core stream interfaces. `PositionedReadable` explicitly promises positional reads that do not change the current stream offset and are thread-safe. `Syncable` distinguishes `hflush`, which makes data visible to new readers, from `hsync`, which is closer to POSIX fsync semantics.
- `ReadOption` is an enum for filesystem read options, and `ZeroCopyUnavailableException` signals failure to provide enhanced zero-copy buffer access.

### Errors, server defaults, shell helpers, and status values

- `FSError` is an `Error` for unexpected native filesystem/disk errors.
- `FSExceptionMessages` centralizes standard stream error strings such as closed stream, negative seek, and seek past EOF.
- `FsServerDefaults` implements `Writable` and carries default values reported from a filesystem service: block size, bytes per checksum, write packet size, replication, file buffer size, encrypted data transfer flag, trash interval, and checksum type.
- `FsStatus` implements `Writable` for capacity, used bytes, and remaining bytes.
- `FsShell.Help` and `FsShell.Usage` are protected shell commands for short usage and long descriptions. `FsShellPermissions.Chmod`, `Chown`, and `Chgrp` expose shell permission command parsing and per-path processing. `Chmod` holds a `ChmodParser`, while `Chown` stores parsed owner and group.

### Hard links and Hadoop Archives

- `HardLink` provides static hard-link operations for Unix/Linux, Windows through winutils, and Mac OS X. Public APIs include `createHardLink`, `createHardLinkMult`, and `getLinkCount`; protected helpers expose command argument length calculations for unit testing. The class documents a move away from the older non-thread-safe `FileUtil` nested class toward static methods that allocate fresh buffers per call.
- `HardLink.LinkStats` exposes mutable public counters for directories, single links, multi-link calls, files linked through multi-link calls, empty directories, and physical file copies. It is explicitly not thread-safe and is intended for knowledgeable clients.
- `HarFileSystem` implements the `har` filesystem over an underlying filesystem. It initializes from URIs such as `har://underlyingfsscheme-host:port/archivepath` or `har:///archivepath`, exposes archive version and hash helpers, resolves archive paths, delegates canonical URI and child filesystem information to the underlying filesystem for delegation-token behavior, and reads archive contents through `_masterindex`, `_index`, and `part-*` files.
- `HarFileSystem` is effectively read-only in this surface. Its docs mark many mutating operations as not implemented: create, non-recursive create, append, replication, delete, mkdirs, local copy into the archive, local output staging, ownership, permissions, and related mutations. `getFileChecksum` returns null because no checksum algorithm is implemented for HAR.
- `HarFs` is an `AbstractFileSystem` adapter via `DelegateToFileSystem`, exposing `getUriDefaultPort`.

### Local filesystem adapters

- `LocalFileSystem` extends `ChecksumFileSystem` for the checksumed local filesystem. It exposes scheme `file`, raw filesystem access, `pathToFile`, local copy helpers, checksum failure quarantine through `reportChecksumFailure`, and local symlink operations.
- `RawLocalFileSystem` extends `FileSystem` for direct local disk access. Its surface includes optional `stat` use, `pathToFile`, local URI/initialization, `open`, `append`, `create`, `createOutputStream`, non-recursive creates, rename, recursive delete, directory creation, primitive mkdir, working directory state, local-output staging, file status, owner/permission/time mutation through native commands or local APIs, symlink support, link status, and link target lookup.

### Paths and path-related exceptions

- `Path` is the central immutable-ish path value type implementing `Comparable`. Constructors accept strings, URIs, parent/child combinations, and scheme/authority/path components. It supports URI conversion, filesystem lookup from `Configuration`, root/absolute checks, parent/name/depth/suffix operations, equality/hash/compare behavior, path qualification, Windows absolute path detection, path merging, and scheme/authority stripping.
- Public `Path` constants include slash separator, separator char, current directory marker, and a `WINDOWS` flag.
- `PathFilter` is the one-method predicate interface for filtering `Path` values.
- `PathIOException` is the base path-aware `IOException` with path, optional target path, optional operation, and formatted message support. Subclasses map to POSIX-like conditions: `PathAccessDeniedException`, `PathExistsException`, `PathIsDirectoryException`, `PathIsNotDirectoryException`, `PathIsNotEmptyDirectoryException`, `PathNotFoundException`, `PathOperationException`, and `PathPermissionException`.
- `InvalidPathException`, `InvalidRequestException`, `ParentNotDirectoryException`, and `UnsupportedFileSystemException` cover invalid path syntax, malformed user requests, parent-not-directory failures, and unsupported filesystem schemes.

### File status, checksum, and operation options

- `LocatedFileStatus` extends `FileStatus` by adding `BlockLocation[]`. It can be constructed from an existing `FileStatus` plus block locations or from full file metadata including optional symlink path.
- `MD5MD5CRC32CastagnoliFileChecksum` and `MD5MD5CRC32GzipFileChecksum` specialize `MD5MD5CRC32FileChecksum` with distinct `DataChecksum.Type` values.
- `Options.ChecksumOpt` carries checksum type and bytes-per-checksum, supports disabled checksums, and has helper methods to merge default and user-provided checksum options while preserving backward compatibility for the older bytes-per-checksum argument.
- `Options.CreateOpts` provides varargs-style create option wrappers: block size, buffer size, replication factor, bytes per checksum, checksum parameter, permissions, create-parent flag, progress callback, and individual `getValue` accessors.
- `Options.Rename` is an enum-like rename option type with byte value conversion.

### Trash and remote iteration

- `RemoteIterator<E>` is a remote-aware iterator whose `hasNext` and `next` can throw `IOException`; it is used by filesystem listing APIs that may fetch results incrementally.
- `Trash` is a configured facade over pluggable trash policies. It can choose the appropriate trash volume for symlinks or mount points using the resolved fully qualified path, move items to trash, create checkpoints, expunge old checkpoints, and provide an emptier runnable intended for superuser execution.
- `TrashPolicy` is the abstract policy contract. Implementations initialize with `Configuration`, `FileSystem`, and home path; report enablement; move paths to trash; create/delete checkpoints; expose current trash directory; and provide an emptier. Protected fields hold the filesystem, trash path, and deletion interval. `getInstance` resolves `fs.trash.classname`.

### XAttrs and crypto streams

- `XAttrCodec` encodes and decodes extended attribute byte arrays for shell, HTTP, and display use. Decoding recognizes `0x`/`0X` hexadecimal, `0s`/`0S` base64, double-quoted text, or unquoted text. Encoding emits quoted text, hex, or base64 according to the requested codec.
- `XAttrSetFlag` validates xattr set semantics against whether an attribute already exists and the supplied `EnumSet` of flags.
- `CryptoFSDataInputStream` wraps an `FSDataInputStream` with a `CryptoCodec`, buffer size, key, and IV.
- `CryptoFSDataOutputStream` wraps an `FSDataOutputStream` with a `CryptoCodec`, buffer size, key, and IV, and exposes `getPos`.

### FTP filesystem

- `FTPException` wraps FTP-related failures in a runtime exception.
- `FTPFileSystem` extends `FileSystem` with scheme `ftp` and uses Apache Commons Net. It exposes initialization from URI/configuration, `open`, `create`, unsupported `append`, `delete`, URI/status/listing operations, mkdirs, rename, working/home directory access, and working directory mutation.
- Public FTP constants include logging, default buffer and block sizes, user/host/port/password configuration prefixes, and `E_SAME_DIRECTORY_ONLY`. The `create` method warns that the returned stream must be closed before using other APIs of the class or calls may block.

### Permission and ACL model

- `org.apache.hadoop.fs.permission.AccessControlException` is deprecated in favor of `org.apache.hadoop.security.AccessControlException`, but remains public for compatibility and remote exception unwrapping.
- `AclEntry` is an immutable ACL entry with type, optional name, permission, and scope. It supports equality/hash/string behavior and static parsing/formatting helpers: `parseAclSpec`, `parseAclEntry`, and `aclSpecToString`.
- `AclEntry.Builder` provides fluent setters for type, name, permission, scope, and `build`; absent scope defaults to access scope.
- `AclEntryScope` and `AclEntryType` are enum types for ACL scope and type.
- `AclStatus` is an immutable ACL status value containing owner, group, sticky bit, and an ordered unmodifiable list of entries. `AclStatus.Builder` sets owner/group/sticky bit and adds one or more entries before `build`.
- `FsAction` is the permission action enum. It exposes symbolic representation, implication checks, boolean-style `and`, `or`, `not`, and `getFsAction` for 3-character strings such as `rwx`.
- `FsPermission` implements `Writable` and models user/group/other actions plus sticky, ACL, and encrypted bits. It can be built from actions, a short mode, another permission, or octal/symbolic string; serialized/deserialized; converted to normal and extended shorts; masked by umask; read from and written to configuration; and produced as default directory, file, cache pool, or compatibility defaults.

### Viewfs configuration and filesystem facade

- `ConfigUtil` provides helpers for viewfs mount table configuration: deriving mount table prefixes, adding default or named mount links, setting home directory config, and reading home directory values.
- `Constants` exposes viewfs config key components: mount-table prefix, home directory key, default mount table name, full prefix for the default table, simple link key, merge link key, merge-slash key, and read-only `PERMISSION_555`.
- `NotInMountpointException` is an `UnsupportedOperationException` for operations on paths not mounted through viewfs.
- `ViewFileSystem` extends `FileSystem` and implements a client-side mount table with the same spec as `ViewFs`. It exposes scheme `viewfs`, constructor paths for `FileSystem#createFileSystem` and direct app use, initialization from URI/configuration, trash location lookup, URI/path resolution, home and working directories, and delegation of common filesystem operations to mounted targets: create, append, delete, block locations, checksum, file status, access, listing, mkdirs, open, rename, owner/permission/replication/time mutation, ACLs, xattrs, checksum toggles, server defaults, content summary, child filesystems, and mount point listing.
- `ViewFileSystem.MountPoint` is visible as a public static marker/data class in this slice, but no members are exposed here.
- The visible start of `ViewFs` extends `AbstractFileSystem`. It has a configuration constructor and begins exposing server defaults, default port, home directory, path resolution, `createInternal`, delete, block locations, checksum, status, access, link status, filesystem status, status iteration, listing, mkdir, open, and internal rename operations. The chunk ends before `ViewFs` is complete.

## Control Flow

`FilterFileSystem` control flow is pure delegation. Construction or initialization installs the wrapped filesystem; all path, stream, metadata, mutation, snapshot, ACL, xattr, checksum, and child-filesystem calls are forwarded unless subclasses override behavior. This makes it the extension point for wrappers that alter scheme handling, metrics, permissions, or other behavior while preserving the underlying filesystem contract.

Stream control flow is split between cursor-based and positional access. `FSDataInputStream.seek` changes the stream cursor, `getPos` reports it, and normal reads consume from it. Positional reads accept an explicit offset and are documented by `PositionedReadable` as not changing the current offset. Enhanced `ByteBuffer` reads use a caller-supplied `ByteBufferPool` and must be paired with `releaseBuffer`. `FSDataOutputStream` writes through its wrapped output stream, while `hflush` and `hsync` establish visibility/durability boundaries.

HAR access flow is index-driven. Initialization binds a HAR filesystem to an archive URI and underlying filesystem. Reads and listings consult `_masterindex` and `_index` to find part files, offsets, lengths, and directory entries. Opening a file returns an input stream that reads the correct segment of a `part-*` file and fakes EOF at the archived file boundary. Block locations are retrieved from the underlying filesystem and adjusted to archive-contained offsets and lengths.

Local filesystem flow differs between checksumed and raw variants. `LocalFileSystem` wraps a raw filesystem with checksum behavior and moves corrupt data/checksum files aside on checksum failures. `RawLocalFileSystem` maps `Path` to `java.io.File`, performs direct local IO, creates directories recursively when requested, and uses local ownership/permission/time and symlink operations where supported.

Trash flow is policy based. `Trash.moveToAppropriateTrash` resolves symlinks or mount points to find the filesystem volume that should own the trash location, then invokes a configured `TrashPolicy`. Policies initialize from configuration and filesystem state, decide enablement, move paths into current trash, checkpoint current trash, delete old checkpoints, and optionally expose a superuser emptier runnable.

Viewfs flow is mount-table based. `ConfigUtil` and `Constants` encode links and home directories into configuration. `ViewFileSystem` or `ViewFs` initializes a client-side mount table from that configuration, resolves an incoming viewfs path to a target filesystem/path, and forwards operations to that target. Operations on non-mounted paths may fail with `NotInMountpointException` or appropriate file/path exceptions. `getChildFileSystems` and mount point access expose the underlying filesystem set for delegation tokens and management.

Permission and ACL flow starts from strings, shorts, builders, or configuration. `FsPermission` converts between action triples and short wire forms, applies umasks, and persists through `Writable`. `AclEntry` parses shell-style ACL specs into immutable entries, builders assemble ACL entries/statuses, and filesystem methods in `FilterFileSystem` and `ViewFileSystem` pass ACL and xattr mutations through to the backing implementation.

FTP flow is remote-session oriented. Initialization configures host, port, user, and password from URI/configuration. File operations issue FTP commands via Commons Net. The `create` documentation is a critical sequencing constraint: the output stream must be closed before another FTPFileSystem API call, or later calls may block.

## State and Persistence Behavior

The XML itself persists API metadata for JDiff. Runtime persistence implied by the APIs includes stream positions, filesystem metadata, permission/xattr/ACL records, trash directories, HAR index files, server defaults, and `Writable` wire forms.

`FilterFileSystem` stores mutable wrapper state in `fs` and optional `swapScheme`. Its behavior depends on lifecycle ordering: callers construct, initialize with URI/configuration, then use delegated operations. `close` propagates cleanup to the wrapped filesystem.

`FSDataInputStream` and `FSDataOutputStream` maintain stream-local state through wrapped stream cursor/position and optional statistics. Enhanced byte buffers have pooled ownership state: callers must release buffers obtained from enhanced reads. Output stream sync calls represent persistence/visibility boundaries for data already written.

`FsServerDefaults`, `FsStatus`, and `FsPermission` implement `Writable`; their fields are intended for RPC or persisted configuration/storage exchange. `FsPermission.toExtendedShort` can encode bits outside classic permission mode, including ACL and encryption indicators, which makes the extended format sensitive for backward compatibility.

`HardLink.LinkStats` is mutable and public, but explicitly not thread-safe. Static hard-link operations themselves are documented as thread-safe after moving away from shared buffers.

`HarFileSystem` state is rooted in persistent archive metadata. `_masterindex` provides hash-range indirection into `_index`; `_index` maps logical paths to part files, offsets, lengths, and directory metadata. HAR permissions are not persisted when creating an archive, so `getFileStatus` reports permissions from archive index files rather than original file permissions.

`RawLocalFileSystem` state includes working directory, local file metadata, and filesystem status from local disk. `LocalFileSystem` adds checksum files and bad-file quarantine behavior. Symlink support depends on platform capability and local implementation support.

`TrashPolicy` stores the target `FileSystem`, trash path, and deletion interval. Trash checkpointing and expunge mutate persistent directories in the filesystem, while `Trash` itself is a configured facade.

`AclEntry` and `AclStatus` are immutable once built. `FsPermission` can be mutable through `fromShort`/`readFields`, but immutable instances are available through `createImmutable`. Umask state is persisted in `Configuration` under current and deprecated labels.

`ViewFileSystem` and `ViewFs` are configuration-backed. Mount tables and home directories live in `Configuration` keys; runtime state is the parsed mount table and working directory. Target filesystem state remains in the mounted filesystems, not in viewfs itself.

## Dependencies and Integration Points

- Core filesystem types depend on `java.io`, `java.net.URI`, Java collections, `Configuration`, Hadoop `Path`, `FileStatus`, `BlockLocation`, `ContentSummary`, `FsStatus`, `FsServerDefaults`, `RemoteIterator`, `Progressable`, `Writable`, and permission/xattr/ACL types.
- Stream APIs integrate with Hadoop stream capability interfaces (`Seekable`, `PositionedReadable`, `ByteBufferReadable`, `HasFileDescriptor`, `CanSetDropBehind`, `CanSetReadahead`, `HasEnhancedByteBufferAccess`, `Syncable`) and `ByteBufferPool`.
- Local filesystem APIs bridge Hadoop `Path` to `java.io.File`, native platform commands/utilities for chmod/chown/stat/symlinks, and checksum quarantine behavior from `ChecksumFileSystem`.
- HAR APIs integrate with underlying filesystems for data reads, block locations, canonical URI, server defaults, and delegation-token child filesystem discovery.
- FTP APIs integrate with Apache Commons Net, Hadoop configuration keys, and the `FileSystem` contract.
- Permission APIs integrate with Hadoop shell parsing (`ChmodParser`), filesystem metadata, configuration, ACL lists, and `org.apache.hadoop.security.AccessControlException` for newer access-control failures.
- Viewfs APIs integrate with configuration naming conventions, mount target URIs, `FileSystem` and `AbstractFileSystem`, delegation-token discovery through child filesystems, trash location selection, and path resolution across mount boundaries.
- Crypto stream wrappers integrate with `org.apache.hadoop.crypto.CryptoCodec`, encryption keys, IVs, and the standard FS data stream wrappers.

## Risks and Edge Cases

- This chunk begins after the start of `FileUtil` and ends inside `ViewFs`. Merge/reconciliation must combine adjacent chunks for complete class-level conclusions.
- `FilterFileSystem` must forward new `FileSystem` methods consistently. Missing delegation for snapshots, ACLs, xattrs, symlinks, checksums, or child filesystems would break wrappers and token discovery.
- Path qualification and scheme swapping are compatibility-sensitive. `Path.isAbsolute` is documented as ambiguous because it returns true even with scheme and authority, so tests must preserve historical behavior.
- `FSDataInputStream` combines cursor reads, positional reads, and pooled byte-buffer reads. Bugs can corrupt stream position, leak buffers, or violate the thread-safety promise of positional reads.
- `FSDataOutputStream.sync` is deprecated but still public. Removing or altering it can break older callers even though `hflush` is the replacement.
- Hard-link multi-create splits command invocations to respect platform command-line limits. Windows, Mac, and Unix command length, path quoting, and link count behavior need platform-specific coverage.
- `HardLink.LinkStats` is public and mutable but not thread-safe; sharing one instance across parallel operations can produce misleading counters.
- HAR is read-only for most mutating operations and does not preserve original permissions. Callers expecting normal filesystem mutation or permission fidelity can fail unless those not-implemented paths are explicit and tested.
- HAR block location adjustment is offset-sensitive; incorrect segment arithmetic can report wrong locality or lengths for files embedded inside `part-*` files.
- Local symlink support and owner/permission mutation depend on platform and native tooling. Windows privilege failures, missing winutils, and command errors are important compatibility cases.
- FTP stream lifecycle is fragile: using other APIs before closing a create stream can block. Rename/delete/list semantics also depend on FTP server behavior and current working directory state.
- `FsPermission.toExtendedShort` can encode ACL and encryption bits beyond traditional mode bits. Consumers that assume only `00000-01777` may silently drop metadata.
- ACL parsing has two modes: with permissions for set operations and without permissions for remove operations. Accepting the wrong form can create incorrect ACL mutations.
- XAttr value decoding accepts multiple textual encodings. Prefix handling, quoted strings, invalid base64/hex, empty values, and round-trip formatting need regression tests.
- Viewfs path resolution crosses filesystem boundaries. Trash location, working directory, child filesystem enumeration, ACL/xattr delegation, and NotInMountpoint failures must all match mounted target behavior.
- `ViewFileSystem` and `ViewFs` expose parallel old and new filesystem APIs. Inconsistent behavior between them can create subtle client differences.

## Test Signals

- API compatibility tests should assert the presence, visibility, checked exceptions, deprecation text, and inheritance/implements lists for `FilterFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `Path`, `RawLocalFileSystem`, `FsPermission`, `AclEntry`, `ViewFileSystem`, and the visible `ViewFs` methods.
- Delegation wrapper tests should use a fake `FileSystem` under `FilterFileSystem` and verify calls forward arguments and return values for create/open/list/delete, ACLs, xattrs, snapshots, symlinks, checksums, server defaults, and child filesystem discovery.
- Stream tests should cover seek, get position, positioned read without cursor movement, readFully EOF behavior, byte-buffer read/release, readahead/drop-behind unsupported cases, `hflush`, `hsync`, and deprecated `sync`.
- Path tests should cover URI construction, parent/child resolution, Windows absolute path detection, scheme/authority stripping, `mergePaths`, root/parent/name/depth behavior, equality/hash/compare, and `makeQualified`.
- Local filesystem tests should cover recursive delete failure on non-empty directories when recursive is false, mkdir existence behavior, create-non-recursive parent handling, local checksum failure quarantine, symlink status versus target status, and owner/permission/time updates.
- HAR tests should validate URI initialization forms, version reading, path hash lookup, index/master-index lookup, file status for files/directories, list status, open segment EOF boundaries, block location offset/length adjustment, null checksum behavior, and explicit failures for unsupported mutations.
- Hard-link tests should cover single links, multi-link splitting at command length boundaries, link counts, missing source/target directories, platform-specific command limits, and public `LinkStats` reporting.
- Permission tests should cover octal and symbolic parsing, `Writable` round trips, immutable creation, umask current/deprecated configuration keys, `toShort` versus `toExtendedShort`, ACL and encrypted bits, action implication/and/or/not, and default directory/file/cache pool permissions.
- ACL tests should cover parsing with and without permissions, default versus access scope, named and unnamed entries, builder defaults, `aclSpecToString` round trips, ordered unmodifiable status entries, and equality/hash behavior.
- XAttr tests should cover text, quoted text, hex, base64, invalid encodings, encode/decode round trips, and `XAttrSetFlag.validate` for create-only, replace-only, and create-or-replace cases.
- FTP tests should use a controllable server or mock to verify initialization from config, open/create stream closure sequencing, list/status conversion, same-directory rename constraints, unsupported append, and working directory handling.
- Trash tests should cover disabled trash, already-in-trash paths, symlink/mountpoint trash resolution, checkpoint creation, expunge behavior, policy factory configuration, and emptier runnable creation.
- Viewfs tests should cover config key generation, adding default and named mount links, home directory config, mount resolution, operations delegated to target filesystems, non-mounted path failures, child filesystem enumeration, mount point listing, trash location, and behavior parity between `ViewFileSystem` and `ViewFs` for overlapping methods.
