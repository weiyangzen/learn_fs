# sources/distributed-fs/beegfs/meta/source/storage/DiskMetaData.h

## Purpose

`DiskMetaData.h` declares the serialization helper for BeeGFS on-disk metadata and defines metadata type IDs and dentry buffer layout constants. It is the shared API used by dentry, file-inode, and directory-inode storage code to encode and decode persistent metadata.

## Important APIs and Types

- `DIRENTRY_SERBUF_SIZE` caps dentry serialization buffers at 4 KiB and must remain no larger than `META_SERBUF_SIZE`.
- `DISKMETADATA_TYPE_BUF_POS` and `DIRENTRY_TYPE_BUF_POS` define fixed byte positions for metadata type and dentry type in serialized buffers.
- `DiskMetaDataType` distinguishes file dentries, directory dentries, file inodes, and directory inodes.
- `DiskMetaData(DentryStoreData*, FileInodeStoreData*)` stores non-owning pointers used for dentry/file-inode serialization.
- Public methods include `serializeFileInode`, `serializeDentry`, `deserializeFileInode`, `deserializeDentry`, and static directory inode serialization/deserialization.
- Private helpers split serialization by dentry format version and provide feature-flag compatibility checks.
- `serializeDirInodeCommonData` is templated so the same field ordering can be used with serializers and deserializers.

## Control Flow and State Contract

`DiskMetaData` is a formatter, not an owner. The caller supplies storage-data objects and buffers, and the formatter mutates those objects during deserialization. Directory inode serialization is static and uses friend access to private `DirInode` fields.

The declaration makes clear that file inodes are currently stored in dentry format, so any future inode-only format would require coordinated updates in code that links inode files into directories.

## Dependencies and Integration Points

The header depends on `FileInodeStoreData` and forward declares `DirInode`, `FileInode`, `DirEntry`, `DentryStoreData`, and `FileInodeStoreData`. It integrates with `DirEntry` and `FileInode` methods that need dentry-format serialization and with `DirInode` metadata storage.

## Risks and Edge Cases

- Because `dentryDiskData` and `inodeData` are raw non-owning pointers, callers must ensure object lifetime exceeds formatter use.
- The fixed buffer-size contract makes large future fields, especially stripe targets and xattrs encoded elsewhere, a compatibility risk.
- New feature flags require updates in both declarations and implementation masks to avoid rejecting newly written metadata.

## Test Signals

Header-level tests should focus on compile coverage and serialization ABI expectations: type values, fixed buffer offsets, buffer-size constraints, and the ability to deserialize through the public API into caller-owned data objects.
