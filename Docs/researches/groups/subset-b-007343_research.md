# subset-b-007343 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileContext.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileContext.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileEncryptionInfo.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileEncryptionInfo.java

## Purpose

`FileEncryptionInfo` is a private Hadoop value object that carries the encryption metadata needed to access an encrypted file. It records the cipher suite, crypto protocol version, encrypted data encryption key, initialization vector, encryption-zone key name, and encryption-zone key-version name.

The class is serializable and immutable by field reference. It is not a cryptographic engine; it is metadata passed between filesystem implementations, clients, and encryption-aware code.

## Important APIs and types

- Constructor: `FileEncryptionInfo(CipherSuite suite, CryptoProtocolVersion version, byte[] edek, byte[] iv, String keyName, String ezKeyVersionName)`.
- Accessors: `getCipherSuite`, `getCryptoProtocolVersion`, `getEncryptedDataEncryptionKey`, `getIV`, `getKeyName`, and `getEzKeyVersionName`.
- Stringification: `toString` and `toStringStable`, both currently rendering the same fields, with EDEK and IV hex-encoded through Apache Commons Codec `Hex`.

## Control flow

Construction is the only meaningful control path. It checks all arguments for non-null values and validates that `iv.length` equals `suite.getAlgorithmBlockSize()`. After validation, all constructor arguments are assigned to final fields.

Getter methods return the stored values directly. `toString` and `toStringStable` build a structured string with cipher/protocol names and hex encodings of the key material bytes.

## State and persistence behavior

The object holds final references to encryption metadata. It implements `Serializable` with a fixed `serialVersionUID`, but it does not define custom Java serialization or Hadoop `Writable` behavior. The `byte[]` fields are not defensively copied on construction or on getter return, so external code retaining the input arrays or mutating arrays returned by getters can change the object's effective contents.

The class exposes EDEK and IV in `toString`/`toStringStable` as hex strings. These are encrypted or public-ish operational metadata rather than plaintext keys, but they remain sensitive diagnostic material.

## Dependencies and integration points

The class depends on `CipherSuite` and `CryptoProtocolVersion` from `org.apache.hadoop.crypto`, Hadoop `Preconditions`, Apache Commons Codec hex encoding, and Java serialization. It is used by filesystem encryption integration points, especially HDFS encryption zones and client-side stream setup that needs key material identifiers and IVs.

`toStringStable` is explicitly preserved for CLI backward compatibility, making its output format part of a user-visible compatibility surface even though the class itself is private audience.

## Risks and edge cases

- Byte-array aliasing allows mutation after construction and through getters.
- `toString` prints hex EDEK and IV, so logs containing this object may expose encryption metadata.
- Only IV length is validated against the cipher suite; EDEK length and key-version naming semantics are left to producers/consumers.
- `toStringStable` currently duplicates `toString`, so future field additions must avoid changing `toStringStable` unless a major compatibility break is intended.

## Test signals

Tests should cover constructor null rejection for every parameter, IV length validation against the selected `CipherSuite`, accessor round trips, byte-array aliasing expectations, stable string output compatibility, and hex rendering of EDEK/IV values. Integration tests should validate that encrypted file status/open paths preserve key name and EZ key-version metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileEncryptionInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileRange.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileRange.java

## Purpose

`FileRange` is the public interface for a byte range used by Hadoop's asynchronous vectored read API, especially `PositionedReadable.readVectored`. It lets callers describe multiple file offsets and lengths, and lets the implementation attach a `CompletableFuture<ByteBuffer>` for each range's eventual data.

The interface also carries an optional opaque reference so higher-level libraries can associate a range with stripe, chunk, request, or application metadata without Hadoop interpreting that value.

## Important APIs and types

- `getOffset()` returns the starting byte offset.
- `getLength()` returns the number of bytes requested.
- `getData()` returns the future holding the range data.
- `setData(CompletableFuture<ByteBuffer>)` is called by vectored-read implementations to attach the asynchronous result.
- `getReference()` returns the optional user/library reference.
- Static factories `createFileRange(long, int)` and `createFileRange(long, int, Object)` instantiate `org.apache.hadoop.fs.impl.FileRangeImpl`.

## Control flow

`FileRange` itself has no implementation control flow beyond the two factory methods. Callers create ranges, pass them to `PositionedReadable.readVectored`, and later inspect `getData()` futures. The read implementation is responsible for validating ranges, scheduling IO, allocating/filling `ByteBuffer` results, and calling `setData`.

## State and persistence behavior

State is implementation-defined by `FileRangeImpl`: offset, length, optional reference, and a mutable future slot for data. The API is in-memory only and has no serialization or persistence contract. The mutable `setData` step is central to its lifecycle: a newly created range may not have data until a vectored read attaches a future.

## Dependencies and integration points

The interface depends on Java NIO `ByteBuffer`, `CompletableFuture`, `PositionedReadable.readVectored`, and the implementation class `FileRangeImpl`. It is an integration point between filesystem input streams and consumers that want to gather non-contiguous file ranges concurrently.

## Risks and edge cases

- The interface does not document validation constraints for negative offsets, negative lengths, or zero-length ranges; enforcement is delegated to `FileRangeImpl` or vectored-read implementations.
- `setData` mutability can be misused by callers after a filesystem has attached a future.
- Future completion semantics, buffer position/limit conventions, exception wrapping, and cancellation behavior are controlled by the read implementation rather than the interface.
- The opaque reference can retain large objects if range objects are kept after reads complete.

## Test signals

Tests should cover factory construction with and without references, validation behavior inherited from `FileRangeImpl`, future attachment and retrieval, vectored read completion for successful and failed ranges, ByteBuffer position/limit expectations, and caller-visible behavior for zero-length or invalid ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileRange.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileStatus.java

## Purpose

`FileStatus` is Hadoop's public, stable client-side metadata record for a filesystem path. It represents file, directory, or symlink type plus length, replication, block size, modification/access times, permissions, owner, group, path, symlink target, and selected attribute flags such as ACL, encryption, erasure coding, and snapshot support.

It is the common status object returned by filesystem listing and stat APIs and is also a compatibility serialization surface through `Writable`, Java `Serializable`, `Comparable`, and `ObjectInputValidation`.

## Important APIs and types

- `AttrFlags` enum: `HAS_ACL`, `HAS_CRYPT`, `HAS_EC`, and `SNAPSHOT_ENABLED`.
- `NONE`: shared empty attributes set.
- `attributes(boolean acl, boolean crypt, boolean ec, boolean sn)`: converts booleans to an `EnumSet` or `NONE`.
- Constructors support legacy minimal metadata, non-symlink filesystems, symlink-aware status, boolean attribute flags, explicit `Set<AttrFlags>`, default construction for deserialization, and a copy constructor that calls getters to support subclasses.
- Type and metadata accessors: `getLen`, `isFile`, `isDirectory`, deprecated `isDir`, `isSymlink`, `getBlockSize`, `getReplication`, `getModificationTime`, `getAccessTime`, `getPermission`, `hasAcl`, `isEncrypted`, `isErasureCoded`, `isSnapshotEnabled`, `getOwner`, `getGroup`, `getPath`, and `getSymlink`.
- Mutators intended for subclasses/deserialization: `setPath`, protected `setPermission`, protected `setOwner`, protected `setGroup`, and public `setSymlink`.
- Object methods: `compareTo(FileStatus)`, compatibility `compareTo(Object)`, `equals`, `hashCode`, and `toString`.
- Serialization: deprecated `readFields`/`write` wrap protobuf conversion through `PBHelper`; `validateObject` enforces required fields after Java deserialization.

## Control flow

Construction normalizes missing permission/owner/group fields. Permission defaults differ by type: directories use `FsPermission.getDirDefault`, symlinks use `FsPermission.getDefault`, and normal files use `FsPermission.getFileDefault`. Owner and group default to empty strings. The constructor asserts that a directory cannot also carry a symlink target.

Type classification is derived from `isdir` and `symlink`: a file is neither directory nor symlink; a directory has `isdir` true and no symlink; a symlink has a non-null `symlink` target. Attribute booleans are read from `attr.contains(...)`.

Equality, hash, and ordering are path-based only. Other metadata differences do not affect comparison or equality.

Deprecated `readFields` reads a size-prefixed `FileStatusProto`, rejects negative sizes, parses it, converts through `PBHelper`, then copies all fields and reconstructs the attribute set. Deprecated `write` converts through `PBHelper`, writes the serialized size, then writes the protobuf bytes. `validateObject` rejects Java-deserialized objects with missing `path` or missing `isdir`.

## State and persistence behavior

The class stores mutable metadata fields directly. It is not deeply immutable: path and symlink can be reset, protected setters update identity metadata, and subclasses may lazily load values. `attr` is stored as the supplied set; the constructor does not defensively copy it. The `NONE` empty set is immutable, while caller-supplied sets may be mutable unless producers pass an immutable set.

`Writable` persistence is protobuf-backed for compatibility but marked deprecated in favor of direct PBHelper/protobuf usage. Java serialization is supported with `serialVersionUID` and object validation.

Because equality and hashing use only `getPath()`, mutating `path` after placing a `FileStatus` in a hash-based collection can corrupt collection behavior.

## Dependencies and integration points

`FileStatus` depends on `Path`, `FsPermission`, `Writable`, protobuf type `FSProtos.FileStatusProto`, and `PBHelper`. It is used by `FileSystem`, `FileContext`, `AbstractFileSystem`, listing APIs, globbing, copy utilities, `LocatedFileStatus`, ViewFs status wrappers, permission checks, and UI/CLI metadata rendering.

The copy constructor deliberately calls getters rather than reading fields directly so wrappers such as `ViewFsFileStatus` can virtualize path/symlink/metadata values.

## Risks and edge cases

- The explicit `Set<AttrFlags>` constructor stores `attr` without null checking or copying; null causes later `hasAcl`/`isEncrypted`/`isErasureCoded`/`isSnapshotEnabled` failures.
- Mutable `attr` sets supplied by callers can change status flags after construction.
- Path-based equality ignores type, length, owner, permissions, and other metadata. This is intentional but can surprise tests comparing full metadata.
- `compareTo(Object)` performs an unchecked cast to preserve binary compatibility, so non-`FileStatus` inputs throw `ClassCastException`.
- `getSymlink` throws `IOException` when the status is not a symlink; `toString` wraps unexpected `IOException` in `RuntimeException`.
- Deprecated `readFields` allocates a byte array of the announced size after only checking for negative values, so corrupt streams with very large positive sizes can cause memory pressure.
- `validateObject` checks only `path` and `isdir`, not permission, owner, group, attr, or directory/symlink consistency.

## Test signals

Tests should cover constructor defaults for file, directory, and symlink statuses; all `AttrFlags` conversions including `NONE`; path-based equality/hash/ordering; copy constructor behavior with overridden getters; `getSymlink` success and failure; `toString` fields for directories/files/symlinks/flags; `Writable` round trips through PBHelper; negative serialized size rejection; Java deserialization validation for missing path/type; mutability expectations for `setPath`, `setSymlink`, and supplied attr sets; and compatibility of deprecated `isDir`/`compareTo(Object)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/fs/FileStatus.java -->
