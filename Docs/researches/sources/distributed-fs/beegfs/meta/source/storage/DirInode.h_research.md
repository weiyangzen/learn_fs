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
