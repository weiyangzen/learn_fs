# sources/distributed-fs/beegfs/meta/source/storage/DiskMetaData.cpp

## Purpose

`DiskMetaData.cpp` implements BeeGFS metadata serialization and deserialization for dentries, file inodes stored in dentry format, and directory inodes. It preserves compatibility across historical on-disk formats while writing current metadata formats with 32-bit node IDs, file-inode version fields, storage pools in stripe patterns, and directory stat flags.

The file is the format boundary between in-memory `DirEntry`, `FileInodeStoreData`, and `DirInode` state and the byte buffers written to xattrs or metadata files by `DirEntry`, `FileInode`, and `DirInode`.

## Important APIs and Functions

- `serializeFileInode` writes a file inode using the dentry-format serializer, choosing `FILEDENTRY` when inlined and `FILEINODE` otherwise.
- `serializeDentry` writes a directory dentry or file dentry based on entry type.
- `serializeInDentryFormat` writes the common dentry header, selects format V3, V4, or V6, sets `DENTRY_FEATURE_32BITIDS`, and dispatches to version-specific serializers.
- `deserializeDentry` reads the dentry header, validates dentry feature flags, strips legacy mirrored flags, dispatches by format version, and backfills owner-node IDs for inlined file formats.
- `serializeDentryV3` and `deserializeDentryV3` handle simple dentry data: entry ID and owner node ID, with 16-bit compatibility when needed.
- `serializeDentryV4` and `deserializeDentryV4` handle older inlined file inodes with old chunk paths and limited feature flags.
- `serializeDentryV6`, `deserializeDentryV5`, `deserializeDentryV6`, and `deserializeDentryV5V6` handle current inlined file metadata, orig UID/parent fields, file state flags, versions, and optional storage pool IDs.
- `deserializeFileInode` currently delegates to `deserializeDentry` because standalone file inodes are still stored in dentry format.
- `serializeDirInodeCommonData`, `serializeDirInode`, and `deserializeDirInode` handle directory inode formats V1 through V3.
- `getSupported*FeatureFlags` and `checkFeatureFlagsCompat` enforce forward-compatibility checks.

## Control Flow

Serialization starts by writing a one-byte metadata type and one-byte storage format version. Dentries then write feature flags, entry type, padding, and version-specific payload. Directory inodes write type, directory format version, feature flags, common data, owner/parent node IDs, and stripe pattern.

Deserialization mirrors this flow. It reads and validates the type/version/feature header, rejects unsupported feature flags by setting the deserializer bad, strips legacy mirror flags that should not be written back, and dispatches to version-specific readers. Older formats are upgraded in memory: V5 file inodes get the default storage pool for later V6 writes, directory formats without storage pools set the default pool, and missing orig UID defaults to current stat UID.

## State and Persistence Behavior

`DiskMetaData` itself does not own state. It holds non-owning pointers to `DentryStoreData` and `FileInodeStoreData`, and its static directory functions operate directly on `DirInode`. Deserialization applies data directly to those objects.

Current write behavior:

- Directory dentries use dentry format V3.
- File dentries without inlined inodes use V3.
- Inlined file dentries and standalone file inodes use V6 unless a V4 case is selected for old orig-feature state.
- Directory inodes use directory format V3 and force `DIRINODE_FEATURE_EARLY_SUBDIRS` plus `DIRINODE_FEATURE_STATFLAGS`.

## Dependencies and Integration Points

The file depends on `Program`, `MirrorBuddyGroupMapper`, storage definitions, `DiskMetaData.h`, `DirInode`, `FileInode`, `DirEntry`, `StripePattern`, `StoragePoolStore`, `StatData` serialization formats, and BeeGFS serializer/deserializer APIs. It is called from the dentry, file-inode, and directory-inode storage paths.

## Risks and Edge Cases

- Compatibility is feature-flag based. Any new on-disk flag must update the supported masks or older readers will reject the metadata.
- V4/V5/V6 inlined file deserialization sets owner node ID manually to either the local node or local buddy group because it is not stored on disk.
- Legacy mirrored fields are discarded and flags removed during deserialization; this is an intentional migration path but may surprise tooling that expects old mirror metadata to survive.
- Serialization buffer limits are enforced by callers checking `Serializer::good`; adding fields can overflow `DIRENTRY_SERBUF_SIZE` or `META_SERBUF_SIZE`.
- `serializeInDentryFormat` contains a V5 auto-upgrade case even though current selection does not write V5 directly.

## Test Signals

Tests should round-trip all supported dentry formats and directory inode formats, validate rejection of unsupported feature flags, verify old 16-bit node ID conversion, confirm storage-pool defaulting for older patterns, ensure owner-node backfill for inlined files in mirrored and non-mirrored mode, and assert serialized size bounds for large stripe patterns and versioned metadata.
