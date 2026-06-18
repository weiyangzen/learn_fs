## sources/distributed-fs/beegfs/meta/source/storage/DentryStoreData.h

Purpose: defines the compact data fields stored on disk for a directory entry and the feature flags that describe dentry/inode encoding.

Important APIs/types: feature flags include `DENTRY_FEATURE_INODE_INLINE`, `DENTRY_FEATURE_IS_FILEINODE`, deprecated `DENTRY_FEATURE_MIRRORED`, `DENTRY_FEATURE_BUDDYMIRRORED`, and `DENTRY_FEATURE_32BITIDS`. `DentryStoreData` stores `entryID`, `entryType`, `ownerNodeID`, and `dentryFeatureFlags`, with protected setters/getters used by friend classes.

Control flow: `DirEntry`, `DiskMetaData`, and `FileInode` mutate and serialize this data. Constructors initialize invalid/zero defaults or full entry metadata.

State and persistence behavior: this is persistent metadata. Comments warn that adding flags requires updating `DiskMetaData::getSupportedDentryFeatureFlags()`.

Dependencies and integration points: depends on storage definitions for `DirEntryType` and `NumNodeID`. It is embedded in `DirEntry` and used by `DiskMetaData` versioned serialization.

Risks: `setDentryFeatureFlags(unsigned)` truncates to `uint16_t`, so new flags must stay within 16 bits. Friend-heavy access means invariants are maintained by surrounding classes rather than this data holder.

Test signals: feature-flag serialization compatibility, 32-bit/modern node ID handling, buddy-mirror flag propagation, and unsupported flag rejection in `DiskMetaData`.
