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
