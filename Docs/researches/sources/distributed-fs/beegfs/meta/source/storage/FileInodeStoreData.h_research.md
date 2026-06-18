# sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.h

## Purpose

`FileInodeStoreData.h` defines the persistent disk payload for file inodes, including stat data, stripe pattern, feature flags, original parent information, CTO version counters, and a compact file-state byte. It is used both for inodes stored separately in the inode tree and for file inode data inlined into directory entries.

## Important APIs and Types

Feature flags include mirrored/buddy-mirrored inodes, original parent ID and UID availability, stat flags, version counters, remote storage target support, and state flags. `FileInodeOrigFeature` records whether original-parent tracking is meaningful for an inode. `AccessFlags`, `DataStates`, and `FileState` encode lower-five-bit access restrictions and upper-three-bit data state. `FileState` exposes predicates for read lock, write lock, unlocked, fully locked, raw value, and data state.

`FileInodeStoreData` owns `StatData`, entry ID, a cloned `StripePattern*`, original UID/parent ID, file and metadata versions, and `rawFileState`. Constructors initialize defaults or clone caller-provided disk data. Methods expose and mutate feature flags, buddy mirror status, remote storage target availability, file state, stat data, entry ID, stripe pattern ownership, original parent metadata, hardlink count, metadata version mirrored into `StatData`, and path info.

## Control Flow and State

The primary constructor clones the stripe pattern and sets `FILEINODE_FEATURE_HAS_ORIG_UID` only when the file UID differs from the parent UID and original metadata is enabled. `setFileInodeStoreData` deep-copies all disk data and clones the pattern after deleting the old one. `setFileState` stores the raw byte and adds or removes `FILEINODE_FEATURE_HAS_STATE_FLAGS` depending on whether the state is nonzero. `getFileState` returns a default unlocked/available state if the feature flag is absent, preserving compatibility with older metadata.

Original parent ID updates are split into dynamic, disk, and persistent setters. Dynamic updates avoid overwriting existing stored original parent information. Persistent updates only write the field and feature flag when original-feature tracking is enabled and the parent ID was not already set.

## Persistence and Dependencies

This is the serialized inode schema, and its feature flags must stay aligned with `DiskMetaData::getSupportedFileInodeFeatureFlags()`. The class depends on `StripePattern`, `StatData`, `PathInfo`, and `Metadata`. It owns its stripe pattern and transfers ownership in `getStripePatternAndSetToNull` or `setPattern` use cases.

## Integration Points

`FileInode` uses this as its durable core. `DirEntry` inlines it into dentries. `MetaStore::mkNewMetaFile`, `mkMetaFileUnlocked`, deinline, reinline, and hardlink paths copy or transfer it. Message handlers and debug tools are friends for efficient metadata extraction.

## Risks and Test Signals

Risks include feature-flag/schema drift, ownership mistakes with `StripePattern*`, stale original-parent fields causing wrong chunk paths, and file-state defaults being misread when the feature flag is absent. Tests should cover clone/copy/destruction ownership, default file-state compatibility, state flag add/remove, buddy mirror flag mutation, original-parent setters, and serialization compatibility when optional flags are absent.
