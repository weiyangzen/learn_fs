# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/dev-support/jdiff/Apache_Hadoop_Common_3.1.2.xml lines 12081-17950

## Research scope

This chunk is a JDiff XML API snapshot for Apache Hadoop Common 3.1.2, not Java implementation source. The range begins in the middle of `org.apache.hadoop.fs.FilterFileSystem`, covers much of the public filesystem API surface, then moves through FTP, ViewFS, HA protocol, protocol-buffer bridge interfaces, HTTP package documentation, and the beginning of `org.apache.hadoop.io` Writable types. Research conclusions below are therefore based on signatures, inheritance, visibility, declared exceptions, constants, and embedded Javadocs.

## Purpose

The chunk documents Hadoop Common's client-side filesystem abstraction layer and adjacent support contracts. It describes how generic `FileSystem` calls are delegated or adapted by wrappers such as `FilterFileSystem`, local implementations such as `RawLocalFileSystem` and `LocalFileSystem`, protocol-backed filesystems such as `FTPFileSystem`, and mount-table based filesystems such as `ViewFileSystem` and `ViewFs`. It also captures stream primitives, path and handle abstractions, quota/status/statistics value objects, trash policy hooks, xattr helpers, storage policy entry points, HA failover/fencing protocols, and the start of Hadoop's serializable `Writable` containers.

## Important APIs and types

The chunk starts with the tail of `org.apache.hadoop.fs.FilterFileSystem`, a delegating `FileSystem` wrapper with protected state `fs` and `swapScheme`. Its methods forward or adapt nearly the full filesystem contract: create/open/append, non-recursive creation, rename/truncate/delete, list status and located status, local-copy helpers, server defaults, file status, ACLs, xattrs, storage policies, snapshot operations, trash roots, and the newer `createFile`/`appendFile` builder entry points. The important integration contract is that subclasses can intercept selected calls while default behavior passes requests to the contained filesystem.

`org.apache.hadoop.fs.FsConstants` defines shared filesystem constants including local, FTP, and ViewFS schemes/URIs and `MAX_PATH_LINKS`, which are scheme-resolution and symlink traversal guardrails.

`FSDataInputStream`, `FSInputStream`, `PositionedReadable`, `Seekable`, `StreamCapabilities`, and `Syncable` define the stream contract. `FSDataInputStream` wraps an input stream and implements seeking, positional reads, byte-buffer reads, enhanced buffer access, file descriptor access, readahead/drop-behind hints, unbuffering, and capability probing. `FSDataOutputStream` wraps output streams and adds position, close, `hflush`, `hsync`, drop-behind, and capability checks. `FSDataOutputStreamBuilder` is the abstract builder for create/append, covering permission, buffer size, replication, block size, recursive parent creation, progress callbacks, checksum options, optional and mandatory FS-specific options, and `build()`.

`FsServerDefaults` and `FsStatus` are `Writable` value objects. Server defaults expose block size, bytes-per-checksum, packet size, replication, file buffer size, encrypted transfer flag, trash interval, checksum type, key provider URI, and default storage policy id. `FsStatus` serializes capacity, used, and remaining bytes.

`GlobalStorageStatistics` stores named `StorageStatistics` instances with synchronized `get`, `put`, `reset`, and iterator methods. `StorageStatistics` supplies a named statistics interface with long-stat iterators, lookup, tracked checks, and reset.

`GlobFilter`, `Path`, `PathFilter`, `PathHandle`, `InvalidPathException`, and `InvalidPathHandleException` form the path-selection and path-identity layer. `Path` supports URI construction, parent/name/suffix operations, qualification, comparison, depth, serialization validation, and cross-platform constants. `PathHandle` is an opaque serializable reference with byte serialization; invalid handles can fail if encoded constraints no longer hold.

`QuotaUsage` records namespace and space quota consumption, storage-type quotas and consumption, string/table formatting helpers, and header constants. `StorageType` exposes storage-media classification helpers such as transient, quota-supporting, movable, parse, list, and static arrays.

`RawLocalFileSystem` implements the raw local disk `FileSystem`: path-to-`File` conversion, URI/initialization, open/append/create/createNonRecursive, output stream creation with permissions, rename, Windows empty-directory rename handling, truncate, delete, list, mkdir helpers, working/home directories, local output staging, status, owner/permission/time mutation, symlink support, link status, and link target. `LocalFileSystem` extends `ChecksumFileSystem`, wraps a raw filesystem, and adds checksum-aware local copy and checksum-failure quarantine behavior.

`LocatedFileStatus` extends `FileStatus` with `BlockLocation[]`, exposing constructors for status-plus-locations, erasure/metadata flags, storage policy sets, `getBlockLocations`, mutation, comparison, equality, and hashing.

`Trash` and `TrashPolicy` define pluggable delete-to-trash behavior. `Trash` constructs against a `Configuration` or specific `FileSystem`, moves paths to the appropriate volume's trash, checkpoints, expunges old checkpoints, exposes emptier runnables, and resolves current trash directories. `TrashPolicy` is the abstract policy with initialization, enablement, move, checkpoint, delete checkpoint, current trash, emptier, and factory methods. It holds protected `fs`, `trash`, and `deletionInterval` state.

`XAttrCodec` encodes and decodes xattr byte values to text, hex, or base64 string forms. `XAttrSetFlag.validate` checks create/replace semantics for xattr mutation.

`org.apache.hadoop.fs.ftp.FTPFileSystem` is a `FileSystem` backed by Apache Commons Net. It exposes FTP-specific configuration constants for user, host, port, password, data connection mode, transfer mode, and same-directory rename behavior. Its API includes scheme/default-port/initialize, open/create, unsupported append, delete, URI, listing, status, mkdirs, rename, and working/home directory handling.

`org.apache.hadoop.fs.viewfs.ViewFileSystem` and `ViewFs` implement mount-table based client-side filesystem views for the old `FileSystem` and newer `AbstractFileSystem` APIs respectively. They resolve logical paths to target filesystems and proxy create/open/append/delete/list/status/block-location/checksum/access/rename/truncate/owner/permission/replication/time/ACL/xattr/snapshot/storage-policy/trash/status/used operations. They also expose mount points, child filesystems, and delegation-token collection. `NotInMountpointException` represents calls against paths that are not mounted through ViewFS. `ViewFileSystemUtil.getStatus` aggregates status across ViewFS paths.

The HA package introduces failover and fencing contracts: `FenceMethod`, `HAServiceProtocol`, `HAServiceProtocolHelper`, `HAServiceTarget`, and exceptions for bad fencing configuration, failed failover, failed health checks, and failed service transitions. `HAServiceProtocol` defines `monitorHealth`, `transitionToActive`, `transitionToStandby`, `getServiceStatus`, and `versionID`. `HAServiceTarget` provides service, health monitor, and ZKFC addresses; fencer access; pre-flight fencing validation; RPC proxy construction; fencing parameter maps; and auto-failover enablement. Protocol bridge interfaces `HAServiceProtocolPB` and `ZKFCProtocolPB` extend generated protobuf blocking interfaces plus `VersionedProtocol`.

The `org.apache.hadoop.io` section starts with `AbstractMapWritable`, `ArrayFile`, `ArrayPrimitiveWritable`, and the opening of `ArrayWritable`. `AbstractMapWritable` is a configurable `Writable` base that carries class-id maps per map instance, supports synchronized class registration and copy, and serializes/deserializes those maps. `ArrayPrimitiveWritable` wraps primitive arrays without copying and serializes them in an optimized wire format. `ArrayFile` is a dense file-based integer-to-value mapping extending `MapFile`.

## Control flow and behavior

Most filesystem operations in this chunk follow a dispatch pattern: a high-level `FileSystem` API method accepts a logical `Path`, resolves or qualifies it, and delegates to an underlying raw filesystem, wrapped filesystem, FTP client, or ViewFS mount target. `FilterFileSystem` is the purest delegator; `ViewFileSystem` and `ViewFs` add a mount-point resolution step and then forward to the resolved target. Local filesystems convert `Path` to `java.io.File` and perform OS-backed operations.

Stream control flow is capability-driven. Input streams support sequential reads, positional reads, and optional enhanced buffer operations; callers are expected to check or tolerate capability failures for readahead, drop-behind, unbuffer, and enhanced byte buffers. Output streams similarly expose flush/sync behavior through `Syncable` and advertised capabilities. `FSDataOutputStreamBuilder` accumulates create/append parameters, separates optional from mandatory FS-specific keys, and defers validation and actual stream creation until `build()`.

Trash behavior is policy-mediated. Delete-like workflows may call `Trash.moveToAppropriateTrash`, which resolves symlinks or mount points so deletion lands in the trash for the actual volume containing the path. Policies create checkpoints, delete old checkpoints, and may provide a superuser emptier runnable.

HA control flow is administrative and RPC-oriented. Health monitors periodically call `monitorHealth`; failover controllers request standby/active transitions; fencing is attempted through an ordered list of configured `FenceMethod` implementations, each validating arguments before use and returning success/failure/indeterminate through `tryFence`.

Writable control flow serializes compact metadata alongside payloads. `AbstractMapWritable` writes class-id mappings with the map instance so nested map writables can be reconstructed without relying on global static class registries. `ArrayPrimitiveWritable` records primitive component type and array data, then reconstructs the wrapped array on read.

## State and persistence behavior

Filesystem state is external to these API objects and resides in backing stores: local disk, FTP server state, mounted target filesystems, or distributed filesystems behind the generic interfaces. The chunk exposes stateful client-side wrappers through fields such as `FilterFileSystem.fs`, `FilterFileSystem.swapScheme`, `TrashPolicy.fs`, `TrashPolicy.trash`, and `TrashPolicy.deletionInterval`. `ViewFileSystem`/`ViewFs` hold mount-table derived state implied by mount-point and child-filesystem APIs.

Persistent metadata surfaces include permissions, owners, groups, modification/access times, ACLs, xattrs, snapshots, storage policies, symlinks, checksums, block locations, quota usage, and filesystem capacity accounting. `FsServerDefaults`, `FsStatus`, `AbstractMapWritable`, and `ArrayPrimitiveWritable` explicitly implement `Writable` serialization, indicating RPC or on-disk/wire persistence contracts.

`PathHandle` is a durable opaque reference whose serialized bytes may include constraints used to verify later access. A later `open(PathHandle)` can fail with `InvalidPathHandleException` if the constraints encoded in the handle no longer hold.

## Dependencies and integration points

The filesystem APIs depend heavily on Hadoop common types: `Configuration`, `Path`, `FileSystem`, `AbstractFileSystem`, `FSDataInputStream`, `FSDataOutputStream`, `FileStatus`, `LocatedFileStatus`, `BlockLocation`, `FsPermission`, `FsAction`, `AclStatus`, `Options` families, `RemoteIterator`, `Progressable`, `DataChecksum.Type`, `Writable`, `Configurable`, and security exceptions. Local filesystem implementations integrate with `java.io.File`, `InputStream`, `OutputStream`, `DataInput`, `DataOutput`, and platform-specific behavior, especially Windows rename handling and symlink support.

`FTPFileSystem` integrates with Apache Commons Net and external FTP server configuration. ViewFS integrates with Hadoop mount-table configuration and target filesystems, including delegation token collection across children. HA types integrate with Hadoop IPC, generated protobuf service interfaces, ZKFC protocol, `NodeFencer`, and service-specific target implementations.

The HTTP package documentation records web UI extension integration via `hadoop.http.filter.initializers`, including static-user filtering.

## Risks and edge cases

The snapshot exposes several compatibility and correctness risks:

- `PositionedReadable` requires thread-safe positioned reads, but its Javadoc warns not all filesystems satisfy that requirement. Callers such as HBase-like stores must verify backing filesystem behavior.
- `FSDataInputStream` and `FSDataOutputStream` expose optional capabilities; unsupported readahead, drop-behind, enhanced byte buffers, unbuffering, `hflush`, or `hsync` can break callers that assume all streams implement them.
- `FSDataOutputStreamBuilder.must(...)` is intentionally strict: unsupported mandatory options should cause `build()` to throw `IllegalArgumentException`, while unrelated optional keys may be ignored.
- `RawLocalFileSystem.listStatus` notes returned listings are not sorted because they rely on `File.list()`. Tests and callers must not depend on order.
- `FTPFileSystem.create` warns that streams must be closed before other APIs are used or calls may block. FTP append is declared unsupported.
- ViewFS operations can fail due to mount resolution, unmapped paths, cross-filesystem semantics, target capability differences, `AccessControlException`, `UnresolvedLinkException`, and aggregation across multiple child filesystems.
- Trash placement is nontrivial for symlinks, mount points, and encryption zones. Older `TrashPolicy.getCurrentTrashDir()` is insufficient for encryption-zone-aware deletes; the path-specific overload is the safer API.
- Fencing is operator-configured and may be vendor-specific. Invalid arguments can be detected at startup or runtime, and a failed or indeterminate fence must be treated as unsafe for failover.
- `AbstractMapWritable` class ids range from 1 to 127, limiting the number of distinct classes in one map instance.
- `ArrayPrimitiveWritable` does not copy the wrapped primitive array, so subsequent caller mutation can change serialized or observed content.
- `Path.validateObject` exists to guard deserialized paths; malformed or malicious serialized objects must be rejected.

## Test signals

Useful test coverage for code using or changing the APIs in this chunk should include:

- Delegation tests for `FilterFileSystem` subclasses proving each overridden operation either transforms arguments intentionally or forwards to the wrapped `FileSystem`.
- Stream conformance tests for seek, positioned read, `readFully` EOF behavior, byte-buffer read/release, capability strings, readahead/drop-behind/unbuffer, and output `hflush`/`hsync`.
- Builder tests that cover create vs append flags, overwrite false on existing files, recursive vs non-recursive parent creation, checksum options, optional option ignoring, mandatory option rejection, and invalid parameter exceptions.
- Local filesystem tests for path-to-file conversion, unsorted listing tolerance, recursive delete errors, mkdir idempotency, chmod/chown/time operations, symlink status vs target status, truncate, Windows rename edge cases, and checksum-failure quarantine.
- FTP tests using a controllable FTP server for open/create/list/status/delete/mkdir/rename and explicit validation that append is unsupported and unclosed streams block or prevent concurrent operations as documented.
- ViewFS/ViewFs tests for mount resolution, NotInMountpoint behavior, delegation across target filesystems, ACL/xattr/snapshot/storage-policy forwarding, trash roots, child filesystem enumeration, delegation tokens, access-control propagation, and cross-mount rename/truncate semantics.
- Trash tests for disabled trash, already-in-trash paths, checkpoint/expunge, path-specific trash locations, symlink and mount-point resolution, and encryption-zone aware current trash lookup.
- HA tests for health monitor address fallback, proxy construction timeouts, RemoteException unwrapping in `HAServiceProtocolHelper`, active/standby idempotence, service failure propagation, fencing parameter injection, bad fencing configurations, and auto-failover flag behavior.
- Writable serialization tests for `FsServerDefaults`, `FsStatus`, `AbstractMapWritable`, `ArrayPrimitiveWritable`, and `ArrayWritable` compatibility, including nested map writables, primitive type preservation, class-id limit handling, and no-copy mutation hazards.
