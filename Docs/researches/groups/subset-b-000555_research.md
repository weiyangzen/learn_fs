# subset-b-000555 research

Grouped research for BeeGFS metadata storage files in `sources/distributed-fs/beegfs/meta/source/storage`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.cpp

## Purpose

`DirEntryStore.cpp` implements the filesystem-backed directory-entry store for a BeeGFS metadata directory. A `DirEntryStore` maps a parent directory ID plus buddy-mirror state to an on-disk dentry directory, creates and removes that directory structure, persists individual `DirEntry` objects, links inode files into directories, removes file and directory dentries, lists directory contents using stable local-filesystem offsets, and updates dentry owner-node information.

The implementation is intentionally thin over POSIX metadata operations: `mkdir`, `rmdir`, `unlink`, `link`, `rename`, `opendir`, `seekdir`, `readdir`, `stat`, and `setxattr`-backed `DirEntry` helpers. It centralizes locking around those operations and adds BeeGFS-specific path derivation, serialization-size-aware listing, and buddy-resync change tracking.

## Important APIs and Functions

- `getDirEntryStoreDynamicEntryPath(parentID, isBuddyMirrored)` selects either the regular dentry root or buddy-mirror dentry root from `Program::getApp()` and builds the parent dentry path with `MetaStorageTk::getMetaDirEntryPath`.
- Constructors initialize `parentID`, `dirEntryPath`, and `isBuddyMirrored`; the default constructor leaves `parentID` as `"<undef>"` until `setParentID`.
- `mkDentryStoreDir(dirID, isBuddyMirrored)` creates the dentry content directory and its ID subdirectory. It returns `SUCCESS`, `EXISTS`, or `INTERNAL`.
- `rmDirEntryStoreDir(id, isBuddyMirrored)` removes the ID subdirectory and the content directory, treating `ENOENT` as non-fatal but logging unexpected errors.
- `makeEntry` and `makeEntryUnlocked` persist a `DirEntry` via `DirEntry::storeInitialDirEntry`.
- `linkInodeToDir` and `linkInodeToDirUnlocked` hard-link a separate inode-file path into the directory under a filename, used for disposal or reinsertion workflows.
- `removeDir` and `removeDirUnlocked` load a dentry, verify it is a directory, and remove it through `DirEntry::removeDirDentry`.
- `unlinkDirEntry` and `unlinkDirEntryUnlocked` remove file dentries through `DirEntry::removeFileDentry`, with caller-supplied unlink flags controlling filename and ID-link deletion.
- `linkEntryInDir` creates a same-directory hardlink between two inlined inode dentries. The caller must have already incremented the file link count.
- `renameEntry` performs a simple same-directory POSIX rename.
- `listIncrementalEx` lists dentries with stable `telldir`/`seekdir` offsets and can stop by serialized response size when `availableRespBufSize` is non-zero.
- `listIDFilesIncremental` lists the dentry-by-ID subdirectory, supporting direct server offsets and a slower incremental-offset fallback for fsck/client seek cases.
- `exists`, `getEntryData`, `dirEntryCreateFromFile`, `setOwnerNodeID`, and `setParentID` are lookup and metadata mutation helpers.

## Control Flow

Most public mutators acquire `rwlock` in write mode, call an `Unlocked` implementation, then release the lock. Read operations use read mode. `mkDentryStoreDir` and `rmDirEntryStoreDir` are static helpers and do not use instance locking because they operate on explicit IDs during lifecycle operations.

Directory-store creation first creates the parent content directory, then creates the dentry-by-ID subdirectory. If the second creation fails, it attempts to remove the first directory before returning an internal error. Removal runs in the reverse order: ID subdirectory first, content directory second.

Listing is offset-driven. `listIncrementalEx` opens the dentry directory, seeks to the caller-provided native offset if non-zero, then loops over `StorageTk::readdirFilteredEx`. For each entry it optionally loads dentry metadata to populate type and entry ID. When `availableRespBufSize` is set, it estimates the serialized contribution of the current entry and stops before overflowing the response budget. The new server offset is the last returned `dirent::d_off`.

`getEntryData` loads a `DirEntry`, optionally copies its inlined `FileInodeStoreData`, clears the source pattern pointer to avoid double deletion, builds `EntryInfo` flags for inlined and buddy-mirrored entries, and returns `SUCCESS` or `PATHNOTEXISTS`.

## State and Persistence Behavior

Persistent state is represented by the local filesystem tree:

- A dentry content directory under either `dentriesPath` or `buddyMirrorDentriesPath`.
- A dentry-by-ID subdirectory derived by `MetaStorageTk::getMetaDirEntryIDPath`.
- Per-entry files and hardlinks written by `DirEntry` methods.

The class keeps in-memory identity fields only: `parentID`, `dirEntryPath`, `isBuddyMirrored`, and an `RWLock`. It does not cache directory contents. All existence, listing, and metadata retrieval go back to disk.

For buddy-mirrored stores, successful creation, deletion, linking, renaming, and metadata changes enqueue changes in `BuddyResyncer::getSyncChangeset()` using `MetaSyncFileType::Directory`, `Dentry`, or `Inode` depending on the object touched.

## Dependencies and Integration Points

This file depends on `Program::getApp()` for configured metadata paths, `MetaStorageTk` for on-disk path layout, `DirEntry` for actual dentry serialization and deletion, `StorageTk` for filtered readdir, `System` and `LogContext` for diagnostics, and `BuddyResyncer` for mirror resync tracking.

`DirEntryStore` is a core component embedded in `DirInode`. `MetaStore` and `DirInode` are friends and call unlocked entry operations during higher-level rename, unlink, and directory lifecycle flows.

## Risks and Edge Cases

- `mkDentryStoreDir` uses `unlink` to remove a directory after ID-subdirectory creation fails; a directory normally requires `rmdir`, so that compensation path may not clean up as intended.
- `listIncrementalEx` computes response size from known list serialization fields but explicitly excludes message-level overhead, relying on the caller to pass a reduced budget.
- Offset behavior relies on local filesystem `d_off` stability. The comment explains this is needed for applications that unlink entries between `readdir` calls.
- `getEntryData` transfers a stripe-pattern pointer out of a temporary `DirEntry` by setting the source pattern to `NULL`; future changes to `FileInodeStoreData` ownership semantics could introduce double-free or leak hazards.
- `linkEntryInDir` requires the caller to adjust link counts before the hardlink operation to avoid crash windows with too-low link counts.
- Buddy-resync additions happen after some locks are released in several methods; the path strings are captured before unlock, but ordering with concurrent operations still matters.

## Test Signals

Useful tests include creating/removing dentry stores in both mirrored and unmirrored paths, exercising failure cleanup for partial directory creation, listing directories while unlinking returned entries, verifying buffer-size-limited listing boundaries, checking dentry-by-ID fsck listing offsets, validating inlined inode metadata returned by `getEntryData`, and confirming buddy-resync change records for directory, dentry, and inode operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.h -->
# sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.h

## Purpose

`DirEntryStore.h` declares `DirEntryStore`, the per-directory dentry store abstraction used by metadata directory inodes, and `ListIncExOutArgs`, the output bundle used for incremental directory listings. The header defines the public API for creating, linking, removing, renaming, listing, querying, and updating dentries while hiding unlocked helpers and filesystem path state.

## Important APIs and Types

- `ListIncExOutArgs` groups output lists for names, entry types, entry IDs, server offsets, and the newest server offset. `outNames` is required; the other lists and pointer are optional.
- `DirEntryStore()` constructs an unbound store with undefined parent ID. `DirEntryStore(parentID, isBuddyMirrored)` binds the store to a metadata path.
- Public mutators include `makeEntry`, `linkEntryInDir`, `linkInodeToDir`, `removeDir`, `unlinkDirEntry`, and `renameEntry`.
- Listing APIs are `listIncrementalEx` for normal dentries and `listIDFilesIncremental` for dentry-by-ID files.
- Query APIs include `exists`, `getEntryData`, `dirEntryCreateFromFile`, and inline helpers `getDentry`, `getDirDentry`, `getFileDentry`, `getEntryInfo`, `getFileEntryInfo`, and `getDirEntryInfo`.
- Static lifecycle helpers are `mkDentryStoreDir` and `rmDirEntryStoreDir`.
- Private unlocked helpers mirror the public methods and assume the caller has the correct lock.
- `removeBusyFile` is a private inline helper used by `DirInode` to move an inlined busy file into a durable inode form while unlinking.

## Control Flow and Locking Contract

The class owns an `RWLock`. Public methods generally lock and delegate to private `Unlocked` variants. Inline lookup wrappers also lock. `getIsBuddyMirrored` is intentionally lock-free because the mirror state should only be set during initialization or controlled conversion. `setParentID` is documented as unlocked and intended for initialization, although it is also used by directory mirror-state conversion.

Friend access is granted to `DirInode` and `MetaStore`, which lets higher-level metadata operations compose directory and inode updates.

## State and Persistence Behavior

The header exposes that the store's state is minimal: a `parentID`, a derived `dirEntryPath`, an `RWLock`, and `isBuddyMirrored`. The persistent data lives in the source-tree-shaped metadata directories and files managed by `DirEntry`, `MetaStorageTk`, and the implementation file. Inline methods always route path-sensitive operations through `getDirEntryPathUnlocked` or `getDirEntryPath`.

## Dependencies and Integration Points

The declaration depends on BeeGFS common storage definitions, `DirEntry`, metadata toolkit types, `EntryInfo`, `FileInodeStoreData`, `NumNodeID`, and list typedefs. `DirInode` embeds this class and uses it for all child dentry operations. `MetaStore` uses friend access for coordinated rename/unlink flows.

## Risks and Edge Cases

- The header relies on callers respecting the unlocked method contract; misuse can bypass `rwlock`.
- `removeBusyFile` is private but callable by friends and couples dentry-store behavior to `DirEntry::removeBusyFile`.
- `ListIncExOutArgs` uses raw pointers and allows optional null outputs; implementation code must check every optional field before writing.
- `getDirEntryPath` returns a copy under lock, while `getDirEntryPathUnlocked` returns a reference. Callers must not retain the reference across state changes.

## Test Signals

Compile-time tests should cover all inline methods, especially null optional list arguments and type-filter helpers. Behavioral tests should assert that public methods acquire locks, that `setParentID` changes both path and mirror state, and that `removeBusyFile` updates the dentry through the expected path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirInode.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/DirInode.cpp

## Purpose

`DirInode.cpp` implements BeeGFS directory inode behavior: default file striping, persistent directory metadata storage and loading, dentry creation/removal/listing delegation, directory counters and stat data, remote storage target metadata, xattr operations, parent/owner updates, and buddy-mirror conversion for contained inlined file inodes.

The class combines durable inode metadata with a `DirEntryStore`. Directory metadata is stored either in a metadata file's extended attribute (`META_XATTR_NAME`) or in file contents, according to `storeUseExtendedAttribs`. Child dentries live in the per-directory dentry directory managed by `DirEntryStore`.

## Important APIs and Functions

- The creation constructor initializes IDs, owner, feature flags, default stripe pattern clone, zero child counters, embedded `DirEntryStore`, and `StatData` for a new directory.
- `createFileStripePattern` and `createFileStripePatternUnlocked` choose storage targets from storage pools and capacity pools, applying default directory settings, caller overrides, buddy-mirror handling, target limits, and optional RAID10 mirror-target rotation.
- `setStripePattern` updates the directory default pattern. Non-root actors may only change default target count and chunk size, not pool or pattern type.
- `setRemoteStorageTarget`, `clearRemoteStorageTarget`, `storeRemoteStorageTargetInfoUnlocked`, `storeRemoteStorageTargetDataBufAsXAttr`, and `loadRstFromFileXAttr` manage remote storage target xattrs and the `DIRINODE_FEATURE_HAS_RST` flag.
- `listIncremental`, `listIncrementalEx`, `listIDFilesIncremental`, `exists`, and `getEntryData` delegate to the embedded `DirEntryStore`.
- `makeDirEntry`, `linkFilesInDirUnlocked`, `linkFileInodeToDir`, `removeDir`, `renameDirEntry`, `unlinkDirEntry`, and `unlinkBusyFileUnlocked` coordinate child dentry changes with directory counters, timestamps, and resync notices.
- `refreshMetaInfo` and `refreshSubentryCountUnlocked` recalculate subdirectory and file counts by listing dentries and reading their types.
- `storeInitialMetaData`, `storeInitialMetaData(defaultACL, accessACL)`, and `storeInitialMetaDataInode` create the dentry store and directory inode file, optionally adding ACL xattrs.
- `storeUpdatedMetaDataBuf*` and `storeUpdatedMetaDataUnlocked` serialize and update directory inode metadata through xattrs, temp-file rename, or in-place fallback.
- `loadIfNotLoaded`, `invalidate`, `loadFromFile`, `loadFromFileXAttr`, `loadFromFileContents`, and `createFromFile` implement lazy and explicit loading.
- `getStatData`, `setStatData`, `setAttrData`, `setDirParentAndChangeTime`, `setOwnerNodeID`, `listXAttr`, `getXAttr`, `removeXAttr`, and `setXAttr` expose inode metadata and xattr operations.
- `setIsBuddyMirrored` flips the directory feature flag, retargets the dentry store path, iterates all inlined dentries, updates their buddy-mirror flags, loads corresponding `FileInode` objects, and updates those inodes.

## Control Flow

Most public methods acquire `rwlock` in read or write mode and call an unlocked helper. Lazy-load paths check `isLoaded` and call `loadFromFile` before using metadata that may not be in memory. `loadFromFile` chooses xattr or file-content deserialization and marks the inode loaded on success.

Directory creation is two-stage. `storeInitialMetaData` creates the dentry directory structure first, then writes the inode metadata file. If inode creation fails after directory creation, it removes the dentry store unless the inode file already exists, which is treated as a successful race. The ACL overload then writes default and access ACL xattrs.

Metadata updates serialize the full `DirInode` through `DiskMetaData::serializeDirInode`. With xattrs enabled, the serialized blob is written to `META_XATTR_NAME`. With content storage, the code writes to a `.update` file and renames it over the inode file. On `ENOSPC` or short writes due to space pressure, it falls back to in-place update after `posix_fallocate`.

Child dentry operations delegate to `DirEntryStore`, then update counters and timestamps if the dentry operation succeeded. Counter update failures are sometimes returned as `INTERNAL` and sometimes only logged depending on operation semantics.

## State and Persistence Behavior

In-memory state includes directory identity, owner and parent node IDs, feature flags, default `StripePattern`, `RemoteStorageTarget`, `StatData`, `numSubdirs`, `numFiles`, `exclusive`, `isLoaded`, `loadLock`, `fileStore`, and the embedded `DirEntryStore`.

Persistent state includes:

- The directory inode metadata file under regular or buddy-mirror inode paths.
- The serialized `DirInode` blob in either `META_XATTR_NAME` or file contents.
- Optional `RST_XATTR_NAME` with serialized remote storage target data, xattr-only.
- The per-directory dentry store directory and dentry-by-ID directory.
- Optional ACL/user xattrs on either the directory dentry path or child file dentry-by-ID path.

The directory stat response derives `nlink` as `2 + numSubdirs` and file size as `numSubdirs + numFiles`, which is important for tools like `find`.

Buddy-mirrored directories enqueue inode, dentry, or directory modifications/deletions in the current buddy-resync changeset after successful durable changes.

## Dependencies and Integration Points

`DirInode.cpp` depends on `Program`, configuration, storage pools, target capacity pools, `Raid0Pattern`, `Raid10Pattern`, `DirEntryStore`, `DirEntry`, `DiskMetaData`, `FileInode`, `MetaStore`, `XAttrTk`, `PosixACL`, and POSIX file/xattr APIs. It is a central integration point for namespace operations in `MetaStore`, fsck-style listing, ACL handling, remote storage target metadata, and buddy mirroring.

## Risks and Edge Cases

- The in-place metadata update fallback reduces the temp-file atomicity guarantee under low-space conditions. It uses `posix_fallocate` to reduce risk, but a crash during in-place write can still be more dangerous than rename.
- `setIsBuddyMirrored` explicitly warns that failure can leave a mix of mirrored and unmirrored contained items; callers need repair or retry handling.
- Counter updates after dentry changes are not always fatal. A successful unlink with failed counter persistence can leave count metadata stale until `refreshMetaInfo`.
- `setRemoteStorageTarget` and `clearRemoteStorageTarget` can update feature flags and xattrs in separate steps, creating possible inconsistency if one succeeds and the other fails.
- `createFileStripePatternUnlocked` returns null for missing storage pools or insufficient targets; callers must translate this to file-creation failure cleanly.
- Non-root `setStripePattern` mutates the existing object partially and restores only by retained clone on store failure; permission checks protect pool and pattern type but not all semantic stripe-policy concerns.
- Xattr methods for child files reference active `FileInode` handles through `MetaStore` to update change time, so lock ordering between directory, metastore, and file handles matters.

## Test Signals

Key tests should cover xattr and file-content metadata modes, create/update/load round trips, low-space update fallback, target selection for normal and buddy-mirror stripe patterns, storage pool missing/insufficient target failures, child dentry counter updates and `refreshMetaInfo`, ACL xattr creation, RST set/clear/load, stat `nlink` behavior, buddy-mirror resync recording, and partial-failure handling in buddy-mirror conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirInode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirInode.h -->
# sources/distributed-fs/beegfs/meta/source/storage/DirInode.h

## Purpose

`DirInode.h` declares BeeGFS directory inode state and API. It defines directory feature flags, a maximum stripe-target limit, the `DirInode` class, and many inline methods used by metadata namespace operations. The class owns persistent directory metadata, an embedded `DirEntryStore`, file-handle tracking, stat counters, stripe defaults, parent identity, buddy-mirror state, and optional remote storage target state.

## Important APIs and Types

- Feature flags include early subdir serialization alignment, legacy mirrored-directory compatibility, stat flags, buddy mirroring, and remote storage target availability.
- `DIRINODE_MAX_STRIPE_TARGETS` caps per-file stripe targets at 256 to keep serialized stripe patterns and chunk-size metadata within safe inode buffer bounds.
- Constructors support new directory creation and deferred load-from-disk construction.
- Public namespace operations include listing, existence checks, dentry creation/link/removal/unlink, owner updates, lazy loading, invalidation, and metadata refresh.
- Stripe and RST APIs include `createFileStripePattern`, `getStripePatternClone`, `setStripePattern`, `setRemoteStorageTarget`, and `clearRemoteStorageTarget`.
- Stat and attribute APIs include `getStatData`, `setStatData`, `setAttrData`, `setDirParentAndChangeTime`, and static `getStatData`.
- Xattr APIs support listing, reading, removing, and setting xattrs on either the directory itself or a file represented by `EntryInfo`.
- Persistence helpers include `storePersistentMetaData`, `storeAsReplacementFile`, `unlinkStoredInode`, and private store/load/remove functions.
- Inline helpers expose dentry and entry-info lookup wrappers and state accessors.

## Control Flow and Locking Contract

The header shows a two-lock model: `rwlock` protects inode state and the embedded dentry store, while `loadLock` protects disk load coordination. Most inline getters acquire `rwlock`. Private `Unlocked` methods require the caller to hold the appropriate lock. `loadIfNotLoadedUnlocked` is the main precondition for mutators that need durable inode state.

Friend classes `MetaStore`, `InodeDirStore`, and `DiskMetaData` can access private fields and helpers for namespace operations, store management, and serialization.

## State and Persistence Behavior

The declared state includes:

- Identity: `id`, `ownerNodeID`, `parentDirID`, `parentNodeID`.
- Policy and optional metadata: `stripePattern`, `rstInfo`, `featureFlags`, `exclusive`.
- POSIX/stat-derived data: `statData`, `numSubdirs`, `numFiles`.
- Concurrency and child entries: `rwlock`, `entries`, `loadLock`, `fileStore`.
- Load lifecycle: `isLoaded`.

Inline counter helpers update timestamps and persist metadata after incrementing or decrementing file/subdir counts. `unlinkStoredInode` removes both dentry-store directory state and inode-file metadata, assuming the directory is already empty.

## Dependencies and Integration Points

The header depends on BeeGFS stripe patterns, remote storage target metadata, storage definitions/errors, stat data, `DirEntryStore`, `MetadataEx`, and `InodeFileStore`. It is consumed by `DirInode.cpp`, `DiskMetaData.cpp`, metastore rename/unlink/create paths, fsck tools, ACL code, and serialization tests.

## Risks and Edge Cases

- Many inline methods wrap `DirEntryStore`, which itself locks internally; higher-level code must avoid lock-order inversions.
- `setIsBuddyMirroredFlag` updates feature flags and resets the embedded store path under the directory lock, but it does not persist by itself.
- `setAndStoreIsBuddyMirrored` calls conversion then persists metadata but ignores the boolean result of `storeUpdatedMetaDataUnlocked`; callers only see the conversion result.
- Counter decrement helpers clamp at zero rather than reporting underflow, which avoids unsigned wrap but can hide earlier count corruption.
- `storeAsReplacementFile` removes an existing metadata file and writes a replacement for fsck; misuse outside repair workflows could drop valid metadata.

## Test Signals

Tests should validate feature-flag serialization compatibility, locked and unlocked helper preconditions, counter persistence and underflow clamp behavior, static `unlinkStoredInode` cleanup order, stripe target limit enforcement, buddy-mirror flag accessors, lazy-load state transitions, and xattr operations for both directory and child-file targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DirInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DiskMetaData.cpp -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DiskMetaData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DiskMetaData.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/DiskMetaData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInode.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/FileInode.cpp

## Purpose

`FileInode.cpp` implements BeeGFS file inode behavior. It covers file metadata serialization/deserialization, dynamic per-target attributes, persistent updates for inlined and standalone inode storage, remote storage target xattrs, open-session counters and access-state checks, POSIX-like attribute changes, hardlink count updates, user xattrs for non-inlined inodes, and append, whole-file, and byte-range lock management.

The file bridges the namespace layer's `EntryInfo` view with two possible persistence layouts: an inode embedded in a dentry, or a separate inode file under the inode hash tree.

## Important APIs and Functions

- Constructors initialize session counters, lock state, dentry compatibility data, and, for loaded inodes, `FileInodeStoreData`.
- `initFileInfoVec` derives per-target `ChunkFileInfo` from file size, stripe pattern, chunk size, sparse-file block data, and stat timestamps.
- `setRemoteStorageTarget`, `clearRemoteStorageTarget`, `storeRemoteStorageTargetUnlocked`, `storeRemoteStorageTargetBufAsXAttr`, `loadRstFromInodeFile`, and `loadRstFromFileXAttr` manage remote storage target metadata and the `FILEINODE_FEATURE_HAS_RST` flag.
- `checkAccessAndOpen` validates file state restrictions and increments read/write session counters atomically under the inode write lock.
- `decNumSessionsAndStore` decrements read/write sessions and persists updated dynamic attributes on close.
- `updateDynamicAttribs`, `serializeMetaData`, and `deserializeMetaData` coordinate dynamic stat data with `DiskMetaData`.
- `storeUpdatedMetaDataBuf*`, `storeUpdatedInodeUnlocked`, and `storeUpdatedInlinedInodeUnlocked` persist inode updates to xattrs, file contents, or the owning dentry.
- `getMetaFilePath` resolves the metadata file path for inlined and standalone layouts.
- `removeStoredMetaData`, `loadFromInodeFile`, `loadFromFileXAttr`, `loadFromFileContents`, `createFromEntryInfo`, `createFromInodeFile`, and `createFromInlinedInode` implement lifecycle and load fallback behavior.
- `setAttrData`, `incDecNumHardLinks`, `listXAttr`, `getXAttr`, `removeXAttr`, and `setXAttr` mutate POSIX metadata and user xattrs.
- `flockAppend`, `flockEntry`, and shared helpers manage exclusive append locks and whole-file shared/exclusive locks.
- `flockRange` and its helpers manage byte-range shared/exclusive locks with wait queues, writer preference, merging, splitting, conflict detection, cancellation, and status dumps.
- `initLocksRandomForSerializationTests` populates lock structures for serialization/equality testing.

## Control Flow

Loading starts from `createFromEntryInfo`. If `EntryInfo` says the inode is inlined, it tries the dentry first and falls back to the inode file; if not inlined, it tries the inode file first and falls back to the dentry. This tolerates stale client-side `EntryInfo`. After load, RST xattrs are loaded when the feature flag is present.

Metadata persistence starts with `storeUpdatedInodeUnlocked`. If the inode is believed to be inlined, it tries to load the parent dentry by ID, copy current inode data into the dentry's inlined store data, and write the dentry. If that reports `INODENOTINLINED`, the object switches to standalone mode and retries as a separate inode file. Standalone writes serialize through `DiskMetaData` and use xattrs or content files depending on configuration.

Content-file updates use temp-file write plus rename for atomic replacement, with in-place fallback on `ENOSPC`. Xattr updates open/create the metadata file and write `META_XATTR_NAME`.

Locking APIs all run under `rwlock` write mode for mutations. New lock requests are deduplicated by `lockAckID`, checked against granted locks and waiters, optionally queued if waiting is allowed, and followed by attempts to grant queued waiters after unlocks or cancellations. Whole-file locks prefer waiting writers before new readers. Range locks also check overlapping waiting writers to avoid writer starvation.

## State and Persistence Behavior

In-memory state includes `inodeDiskData`, per-target `fileInfoVec`, session counters, exclusive TID, dentry compatibility data, inlined-state flag, parent-reference tracking, remote storage target info, and several granted/waiting lock containers for append, whole-file, and range locks.

Persistent state includes:

- The serialized file inode, either in the owning dentry or in a separate inode metadata file.
- Dynamic file attributes folded into `StatData` before serialization.
- Optional remote storage target data in `RST_XATTR_NAME`.
- User xattrs for non-inlined inode files only.

Buddy-mirrored standalone inode updates and deletes enqueue inode modifications/deletions in the buddy resync changeset. Xattr mutations also enqueue inode modifications, with FIXME comments noting the resync granularity is broader than just the xattr.

## Dependencies and Integration Points

The implementation depends on `DiskMetaData`, `DirEntry`, `EntryInfo`, `FileInodeStoreData`, `Locking.h`, `XAttrTk`, BeeGFS serialization, `MetaStorageTk`, `Program` paths/configuration, `RemoteStorageTarget`, POSIX file and xattr APIs, and lock-detail types. It is used by metadata open/close, setattr, unlink-busy-file, hardlink, lock, RST, and xattr workflows.

## Risks and Edge Cases

- `getMetaFilePath` constructs the inlined dentry-by-ID path by concatenating `MetaStorageTk::getMetaDirEntryIDPath(dirEntryPath)` and `entryID`; this relies on the helper returning a path with the correct separator.
- Inlined-to-standalone fallback in `storeUpdatedInodeUnlocked` handles unexpected layout changes, but it logs a locking warning because the write lock should normally prevent this state drift.
- In-place update fallback on low disk space has weaker crash behavior than temp-file rename.
- `clearRemoteStorageTarget` clears the feature flag and persists before removing the xattr; xattr removal failure is logged but not returned as failure.
- User xattr methods assert that inlined inodes cannot access their own xattrs; callers must route inlined file xattr operations through `DirInode`/dentry paths.
- Lock queues can grow with waiters; cancellation by client or handle is critical for cleanup on disconnect/close.
- Writer preference avoids starvation for writers but can delay readers behind queued exclusive requests.
- Range-lock merging/splitting mutates ordered sets; comparator consistency with modified ranges is essential because entries are erased and reinserted around changes.
- `initFileInfoVec` assumes valid stripe patterns and chunk sizes. Corrupt metadata can lead to bad per-target calculations if deserialization validation misses it.

## Test Signals

Important tests include load fallback between inlined and standalone layouts, serialize/deserialize round trips for sparse and non-sparse files, dynamic attribute recalculation across stripe target counts, xattr and content metadata modes, low-space in-place fallback, RST set/clear/load behavior, open access checks for read/write/full lock states, session counter decrement persistence, setattr rollback on store failure, hardlink count rollback, buddy-resync records, non-inlined user xattrs, append and whole-file lock wait queues, range-lock overlap/merge/split/unlock behavior, cancellation by handle/client, duplicate lock request handling, writer-preference behavior, and randomized lock serialization equality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInode.cpp -->
