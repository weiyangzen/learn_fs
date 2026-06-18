# subset-b-000556 Research

Grouped research for BeeGFS metadata storage files under `sources/distributed-fs/beegfs/meta/source/storage`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInode.h -->
# sources/distributed-fs/beegfs/meta/source/storage/FileInode.h

## Purpose

`FileInode.h` declares the in-memory representation of non-directory file inodes on the metadata server. It wraps the persistent `FileInodeStoreData` with runtime-only state: dynamic storage-node attributes, open-session counters, local exclusive-operation ownership, POSIX-style append/flock/range locks, remote storage target information, and parent-store references. It is a central integration point for file metadata persistence, dentry-inline compatibility, session close handling, hardlink/deinline behavior, and HSM-like file state gating.

## Important APIs and Types

`DentryCompatData` carries dentry type and feature flags needed when writing inode data in dentry-compatible format. `FileInode::LockState` serializes the currently granted lock state for recovery or tests, deliberately excluding waiter queues. The public constructors support empty deserialization and construction from disk data plus dentry metadata. Important public methods include `createFromEntryInfo`, `serializeMetaData`, `deserializeMetaData`, `updateInodeOnDisk`, `updateInodeOnDiskIncrementVersion`, xattr methods, remote-storage-target methods, file-state methods, session counters, `getStatData`, hardlink helpers, lock acquisition/cancellation APIs, and clone support.

## Control Flow and State

Most accessors lock `rwlock` directly or through `UniqueRWLock`/`RWLockGuard`. Static `createFromEntryInfo` dispatches to inlined or inode-file loading paths. Metadata updates flow through `storeUpdatedInodeUnlocked`, which chooses inlined-dentry or standalone-inode persistence. Dynamic attributes are accumulated in `fileInfoVec` and folded into `StatData` on stat or close rather than written for every update. Session state is split into read sessions and write or read-write sessions, and `closeFile` paths call `decNumSessionsAndStore`.

File locks are maintained in separate append, whole-file, and byte-range queue sets. Entry locks compare client node and client file descriptor, while range locks compare client node and owner PID. File state is stored as a raw byte in `FileInodeStoreData`; `setFileState` validates transitions against active sessions before persisting. Parent references keep a directory alive while an inode is held from a per-directory `InodeFileStore`.

## Persistence and Dependencies

This header depends on storage formats (`StripePattern`, `RemoteStorageTarget`, `StatData`, `PathInfo`, `ChunkFileInfo`), threading (`RWLock`, `SafeRWLock`, `UniqueRWLock`, atomics), serialization, `Locking.h`, `DiskMetaData`, and dentry/inode storage data. It bridges on-disk representations stored as xattrs or file contents and inlined dentry metadata. Feature flags for buddy mirroring, original parent/UID, CTO versions, RSTs, and state flags determine serialized shape and compatibility.

## Integration Points

`MetaStore` and `InodeFileStore` are friends and drive loading, reference movement, unlink, rename, open, close, hardlink, and state changes. `SessionFile` uses the lock APIs. `DirEntry`/`DirEntryStore` consume the dentry-compatible store data. Global inode locks call `createFromEntryInfo` and may hold references outside normal client paths.

## Risks and Test Signals

Risks cluster around lifetime and concurrency: stale client inline flags, non-inlined inodes temporarily loaded in a directory store, active session counters versus file-state transitions, and lock waiter duplicate tracking. `checkTargetIsActiveInPattern` can be sensitive to small-file/chunk math and stripe pattern assumptions. Tests should cover serialization/deserialization, random lock-state serialization, file state transitions with read/write sessions, xattr versus content persistence, remote storage target persistence, deinline/reinline metadata flags, and stale EntryInfo inline flag recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.cpp

## Purpose

`FileInodeStoreData.cpp` implements the small non-inline parts of `FileInodeStoreData`: path-info extraction and equality. The file is the bridge between stored original-parent metadata and the `PathInfo` object used by chunk path calculation and fsck-style inspection.

## Important APIs and Types

`FileInodeStoreData::getPathInfo(PathInfo*)` converts `FileInodeOrigFeature` into `PATHINFO_FEATURE_ORIG`, no flag, or `PATHINFO_FEATURE_ORIG_UNKNOWN`. It then sets original parent UID and original parent entry ID on the output `PathInfo`. `operator==` compares inode feature flags, `StatData`, entry ID, stripe pattern equivalence, original-feature state, original UID, and original parent entry ID.

## Control Flow and State

`getPathInfo` uses a `switch` over `origFeature`. The unset/default case logs an error because callers expected the dentry version or stored metadata to identify whether original-parent fields are meaningful. Equality delegates stripe comparison to `stripePatternEquals`, so it expects both objects to own valid stripe-pattern pointers.

## Persistence and Dependencies

The implementation depends on `FileInodeStoreData.h`, `PathInfo`, and logging through `LogContext`. The path info reflects stored metadata fields that are later used to locate storage chunks, especially after UID or parent changes.

## Integration Points

`FileInode::getPathInfo` calls into this method under the inode lock. Fsck enumeration in `MetaStore` also depends on file inode path info when building `FsckFileInode` records. Equality is primarily useful for serialization tests and metadata comparisons.

## Risks and Test Signals

The important risk is losing original parent data or leaving `origFeature` unset, which would make chunk paths ambiguous. Equality can dereference stripe patterns and should be exercised with valid cloned patterns. Tests should include all three `FileInodeOrigFeature` cases and compare objects with different flags, stat data, and stripe patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/FileInodeStoreData.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.cpp

## Purpose

`GlobalInodeLockStore.cpp` implements a process-wide map of file inodes reserved for internal metadata operations. It prevents normal metadata paths from loading or mutating the same inode while operations such as chunk rebalancing or file-state updates require exclusive coordination.

## Important APIs and Functions

`opTypeToString` formats `LockOperationType`. `insertFileInode` loads an inode from `EntryInfo`, inserts a `GlobalInodeLockEntry`, validates operation-type compatibility, optionally increments the reference count, and emits file events. `releaseFileInode` and `releaseFileInodeUnlocked` validate the operation type before releasing references and deleting the entry at refcount zero. Lookup and accessor methods include `lookupFileInode`, `getFileInode`, and `getFileInodeUnreferenced`. Maintenance APIs include `updateInodeLockTimesteps`, `clearLockStore`, `clearLockStoreByOpType`, and operation-filtered counters.

## Control Flow and State

All map mutation is guarded by `rwlock` in write mode. Inserts are keyed by entry ID. Existing entries are accepted only when the requested operation type matches the stored type; different operation types receive `FhgfsOpsErr_INODELOCKED`. New entries call `FileInode::createFromEntryInfo`, wrap the object in an `ObjectReferencer`, and initialize elapsed time to zero. Reference increments are explicit, and `getFileInode` resets the timeout counter when a new reference is taken.

Timeout cleanup iterates only entries of the requested operation type, adds elapsed seconds, and force releases entries past the configured max. Clear operations delete referencers and entries directly.

## Persistence and Dependencies

The store itself is memory-only, but it holds fully loaded `FileInode` objects whose persistence APIs may be called by the owning operation. It depends on `Program::getApp`, `FileEventLogger`, `FileInode`, `EntryInfo`, and `RWLockGuard`. Event logging uses `makeEventContext` and records `INODE_LOCKED` style events when callers provide a `FileEvent`.

## Integration Points

`InodeFileStore::referenceFileInodeUnlocked` checks this store before loading from disk in normal paths. `MetaStore::setFileState` inserts with `LockOperationType::FILE_STATE_UPDATE` and bypasses normal lock-store checks while referencing the locked inode. Chunk balancing uses the chunk-rebalancing operation type.

## Risks and Test Signals

The main risk is leaked global locks on error paths; the code logs severe messages because such leaks can block inode access until metadata service restart. Operation-type mismatches protect unrelated internal operations but require every release to pass the same type used at insert. Timeout release may leave orphaned chunks and logs fsck guidance. Tests should cover same-op refcount sharing, different-op rejection, release mismatch failure, timeout cleanup by operation type, event logging on insert, and cleanup when inode creation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.h -->
# sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.h

## Purpose

`GlobalInodeLockStore.h` declares the global internal-operation inode lock store. The "lock" is represented by successful insertion into a process-wide map and a reference-counted `FileInode`, not by a kernel or POSIX file lock.

## Important APIs and Types

`LockOperationType` currently distinguishes `CHUNK_REBALANCING` and `FILE_STATE_UPDATE`. `GlobalInodeLockEntry` groups the inode referencer, operation type, and elapsed-time counter so parallel side maps cannot diverge. `GlobalInodeLockStore` exposes insert, release, lookup, referenced and unreferenced accessors, timeout update, full cleanup, operation-specific cleanup, and counters.

## Control Flow and State

The class owns `GlobalInodeLockMap inodes` and an `RWLock`. Private helpers centralize operation-string formatting, unlocked release, refcount increase/decrease, and timeout reset. The destructor calls `clearLockStore`, so all held inode references are deleted on store destruction.

## Persistence and Dependencies

The header depends on `FileInode`, `ObjectReferencer`, file event logging, and common storage errors. It has no durable state of its own, but it loads durable inode metadata and blocks regular load paths while entries are present.

## Integration Points

`MetaStore` contains one `GlobalInodeLockStore` and exposes it through `getInodeLockStore`. `InodeFileStore` consults it when `checkLockStore` is true. State update and chunk balancing code use operation types to avoid clearing each other's locks.

## Risks and Test Signals

Operation type must be threaded consistently through insert, release, timeout, and cleanup. Adding a new operation type requires extending `opTypeToString` and validating all callers. Tests should verify public counters, selective cleanup, destructor cleanup behavior, and interaction with regular `InodeFileStore` loads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.cpp

## Purpose

`IncompleteInode.cpp` implements a small RAII wrapper used during buddy resync to create a raw metadata inode and then fill its metadata content or xattrs. It supports incremental construction before the metadata object is considered complete.

## Important APIs and Functions

The destructor closes the owned file descriptor and logs close failures. `setXattr` writes an xattr with `fsetxattr`, records the xattr name in `xattrsSet`, and converts `errno` to `FhgfsOpsErr`. `setContent` writes either xattrs or file contents depending on configuration. `clearUnsetXAttrs` lists existing xattrs and removes user namespace attributes not set through this object. `fileName` resolves `/proc/self/fd/<fd>` for logging.

## Control Flow and State

`setContent` delegates to `setXattr` when extended attributes are enabled. When xattrs are disabled, only `META_XATTR_NAME` may be represented as file contents; other attributes return `FhgfsOpsErr_INVAL`. Repeated content writes truncate the file to the new size before writing. `clearUnsetXAttrs` builds a set from `flistxattr`, skips attributes already set, and removes only `user.*` attributes, deliberately leaving system, trusted, and security namespaces alone.

## Persistence and Dependencies

The file uses POSIX fd APIs (`fsetxattr`, `flistxattr`, `fremovexattr`, `ftruncate`, `write`, `readlink`, `close`) and `Program::getApp()->getConfig()->getStoreUseExtendedAttribs()`. It is persistent only through the fd supplied by `MetaStore::beginResyncFor`.

## Integration Points

`MetaStore::beginResyncFor` returns `IncompleteInode` to the buddy resyncer. The resync caller fills metadata through `setContent` and `setXattr`, then can call `clearUnsetXAttrs` to remove stale user metadata from preexisting files or directories.

## Risks and Test Signals

Partial writes are treated as errors but do not retry, so tests should simulate short writes if possible. The content mode only supports one metadata payload and should reject arbitrary attributes. Tests should cover move construction/assignment, fd close behavior, xattr cleanup filtering, repeated content truncation, and xattr-disabled mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.h -->
# sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.h

## Purpose

`IncompleteInode.h` declares the RAII object used while raw metadata is being reconstructed, especially for buddy resync. It represents an open metadata file or directory that can still receive content and xattrs.

## Important APIs and Types

`IncompleteInode` owns an integer fd, a `hasContent` flag, and a set of xattr names written during the current fill pass. Copy construction and copy assignment are disabled. Move construction and move assignment transfer ownership through `swap`. Public mutation methods are `setXattr`, `setContent`, and `clearUnsetXAttrs`.

## Control Flow and State

The default object has fd `-1` and no content. Move assignment uses copy-and-swap with a temporary constructed from the moved source, leaving only one live object owning the descriptor. The private `fileName` helper exists for diagnostic output.

## Persistence and Dependencies

The class depends only on storage error definitions in the header, with implementation details in the cpp. It does not know the metadata path directly; it owns only the fd returned by `open` or `mkdir` plus `open`.

## Integration Points

Instances are produced by `MetaStore::beginResyncFor` and then consumed by resync logic. Because it is move-only, callers can return it in `std::pair<FhgfsOpsErr, IncompleteInode>` without accidental descriptor duplication.

## Risks and Test Signals

Callers must check the accompanying error code before writing to a default fd `-1` object. Tests should verify that moves do not double-close fds, default objects are harmless, and cleanup removes only attributes absent from `xattrsSet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/IncompleteInode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.cpp

## Purpose

`InodeDirStore.cpp` implements the directory-inode cache/reference store for the metadata server. It loads `DirInode` objects on demand, reference-counts them, maintains a configurable reference cache, supports stat/setattr/remove operations, and invalidates mirrored directories after role or consistency changes.

## Important APIs and Functions

The constructor reads cache limits from config. `referenceDirInode` finds, creates, optionally force-loads, references, and cache-adds directory inodes. `releaseDir` and `releaseDirUnlocked` drop references and delete entries when no references remain. `removeDirInode` removes cache state, checks removability, and unlinks persistent directory metadata. `stat`, `setAttr`, `invalidateMirroredDirInodes`, `getSize`, `getCacheSize`, and `cacheSweepAsync` provide operational access.

Private helpers include `insertDirInodeUnlocked`, `isRemovableUnlocked`, `cacheAddUnlocked`, `cacheRemoveUnlocked`, `cacheRemoveAllUnlocked`, and `cacheSweepUnlocked`.

## Control Flow and State

`referenceDirInode` starts with a read lock, upgrades to write only if the directory is missing, and inserts a new `DirectoryReferencer` when needed. If `forceLoad` is true, it loads the inode after releasing the store lock and releases it again if disk load fails. Cache insertion takes an extra reference, so cached directories stay alive until swept or explicitly removed. `releaseDirUnlocked` refuses to delete a directory whose embedded file store still has references unless the app is terminating.

`stat` checks owner identity for loaded directories and falls back to static `DirInode::getStatData` when absent. `setAttr` either applies directly to a loaded non-exclusive directory or temporarily loads a stack `DirInode`.

## Persistence and Dependencies

Persistent operations delegate to `DirInode::loadFromFile`, `DirInode::unlinkStoredInode`, `DirInode::getStatData`, and `DirInode::setAttrData`. The store depends on `Program`, config, POSIX ACL support, threading guards, and `DirInode`.

## Integration Points

`MetaStore` owns `dirStore` and calls it for directory references, stat, setattr, removal, cache stats, and cache sweeps. `DirInode` embeds an `InodeFileStore`, so directory release must account for file references held through `MetaFileHandle`.

## Risks and Test Signals

Key risks are lock-order deadlocks, cache references masking removability, owner mismatch for mirrored/root directories, and deleting directories while child file references remain. Tests should cover reference/release balance, force-load failure cleanup, cache sweep thresholds, removing loaded/nonloaded directories, mirrored invalidation, and `releaseDir` error logging when fileStore is non-empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.h -->
# sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.h

## Purpose

`InodeDirStore.h` declares the metadata server store for directory inodes. It is the directory counterpart to `InodeFileStore`, but uses `AtomicObjectReferencer` and an additional cache map because directory references are frequent and many client operations only need lightweight locking.

## Important APIs and Types

`DirectoryReferencer` is an `AtomicObjectReferencer<DirInode*>`. `DirectoryMap` stores owned directory referencers keyed by directory ID. `DirCacheMap` stores cached raw `DirInode*` values keyed by the same ID. Public APIs reference/release directories, test in-store state, remove persistent directory inodes, stat/setattr directories, invalidate mirrored directories, inspect reference/cache sizes, and trigger async cache sweeping.

## Control Flow and State

The class owns `dirs`, synchronous and asynchronous cache limits, a random generator for sweep starting points, `refCache`, and `rwlock`. Copy and move are explicitly deleted to keep referencer and cache ownership stable. The destructor clears cache references and all directory referencers.

## Persistence and Dependencies

The header depends on common storage and threading types plus `DirInode` forward declaration. Persistent disk behavior is delegated to `DirInode`, but this store determines when objects are loaded, kept cached, or removed.

## Integration Points

`MetaStore` is a friend and owns an instance. `DirInode` is also a friend, allowing tight integration with per-directory file stores and directory metadata internals.

## Risks and Test Signals

The extra cache reference means tests should verify release counts when cache entries are added and removed. Any change to cache limits or sweep strategy can affect memory pressure and latency. Tests should confirm destructor cleanup, disabled cache behavior, sync and async sweep behavior, and directory removability when loaded, cached, exclusive, or non-empty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.cpp

## Purpose

`InodeFileStore.cpp` implements reference-counted storage for loaded `FileInode` objects. One instance exists globally in `MetaStore`, and each `DirInode` has a per-directory instance. The implementation handles file reference/open/close, stat/setattr, unlink, remote move serialization, hardlink count changes, global lock-store exclusion, and race repair around stale inline flags.

## Important APIs and Functions

Lookup and reference APIs include `isInStore`, `referenceLoadedFile`, `referenceFileInode`, `referenceFileInodeUnlocked`, `referenceFileInodeMapIterUnlocked`, and `getReferencerAndDeleteFromMap`. Lifecycle APIs include `releaseFileInode`, `closeFile`, `clearStoreUnlocked`, `loadAndInsertFileInodeUnlocked`, `insertReferencer`, and `deleteUnreferencedInodeUnlocked`. Mutation APIs include `openFile`, `stat`, `setAttr`, `unlinkFileInode`, `moveRemoteBegin`, `moveRemoteComplete`, `isUnlinkable`, and `incDecLinkCount`.

## Control Flow and State

The store owns a map from entry ID to `FileInodeReferencer*` protected by `rwlock`. `referenceFileInodeUnlocked` checks the map, optionally loads from disk, and normally refuses to load when `GlobalInodeLockStore` contains the inode. Internal operations can pass `checkLockStore=false`. `referenceFileInodeMapIterUnlocked` refuses references if another thread owns the inode's exclusive TID.

`openFile` references the inode, calls `FileInode::checkAccessAndOpen`, and releases the reference on access failure. `closeFile` persists dynamic metadata via `decNumSessionsAndStore`, detects the last writer close, and decrements the referencer. `unlinkFileInodeUnlocked` checks unlinkability, optionally clones an unreferenced inode for the caller, and removes persistent metadata. Remote move begin serializes an unreferenced inode, sets exclusive TID, persists original parent ID, and appends RST data if present. Remote complete deletes the unreferenced inode entry.

## Persistence and Dependencies

Persistent load/store is delegated to `FileInode::createFromEntryInfo`, `FileInode::unlinkStoredInodeUnlocked`, `FileInode::setAttrData`, `FileInode::incDecNumHardLinks`, and close/update methods. The implementation depends on `Program` to access `MetaStore` and its `GlobalInodeLockStore`.

## Integration Points

`MetaStore` uses the global store for non-inlined inodes and as the target when references move out of per-directory stores. `DirInode` uses a per-directory store for inlined inode objects. `MetaStoreRename` uses move begin/complete during remote rename. `GlobalInodeLockStore` blocks normal loads through `lookupFileInode`.

## Risks and Test Signals

The most important race is deletion of an inode still referenced through another store; `deleteUnreferencedInodeUnlocked` explicitly checks refcount to avoid use-after-free during rename/hardlink/open races. Non-inlined inodes found in directory stores are treated as in-use and cleaned up to restore global-store invariants. Tests should cover global lock rejection, bypass for internal state update, exclusive TID behavior, open failure release, last-writer detection, unlink in-use cases, remote move begin/complete, and stale inline flag recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.h -->
# sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.h

## Purpose

`InodeFileStore.h` declares the reference-counted in-memory store for file inodes. It is used for all non-directory file-like entries, both in the global `MetaStore` and inside each `DirInode` for inlined inode metadata.

## Important APIs and Types

`FileInodeReferencer` is an `ObjectReferencer<FileInode*>`. `InodeMap` maps entry ID strings to referencers. `FileInodeRes` returns a raw inode pointer plus `FhgfsOpsErr`. Public methods cover store lookup, reference, release, unlink, open/close, stat, setattr, remote move begin/complete, size, and unlinkability checks.

Private methods manage unlocked reference paths, refcount decrement, unreferenced inode lookup, unreferenced deletion, load/insert, referencer migration, map-iterator reference, and link count changes. Inline `incLinkCount` and `decLinkCount` wrap `incDecLinkCount`.

## Control Flow and State

The store owns an `InodeMap` and an `RWLock`. Public methods take appropriate locks and delegate to unlocked variants where `MetaStore` or `DirInode` already holds wider locks. `getReferencerAndDeleteFromMap` and `insertReferencer` are intentionally exposed only to friends so `MetaStore` can move loaded inodes from a per-directory store to the global store.

## Persistence and Dependencies

The header depends on `FileInode`, `GlobalInodeLockStore`, metadata toolkit types, and storage error definitions. Actual persistence is in `FileInode`; this class controls whether an inode is loaded and when the owned referencer is deleted.

## Integration Points

`DirInode` and `MetaStore` are friends and coordinate store migration, unlinking, open/close, and hardlink operations. Normal external users do not access the map directly.

## Risks and Test Signals

Because methods return raw `FileInode*` backed by a referencer, every successful reference must be paired with release/close. Store migration must preserve references and parent directory lifetimes. Tests should cover referencer migration, destructor cleanup with open sessions, unlinkability semantics, and locked inode access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/Locking.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/Locking.cpp

## Purpose

`Locking.cpp` implements equality and randomized test initialization for file lock detail structures declared in `Locking.h`. The actual lock algorithms live in `FileInode`; this file provides value semantics and test support for serialized lock state.

## Important APIs and Functions

`EntryLockDetails::operator==` compares client node ID, client file descriptor, owner PID, lock ack ID, and lock type flags. `RangeLockDetails::operator==` compares client node ID, owner PID, lock ack ID, lock type flags, and inclusive start/end range. `initRandomForSerializationTests` for both structures fills fields with random IDs, flags, ranges, and alphanumeric ack IDs.

## Control Flow and State

The implementation is straight-line. Random initialization uses `Random` and `StringTk::genRandomAlphaNumericString`. It does not validate that generated range start is less than or equal to end, because serialization tests only need nonconstant field coverage.

## Persistence and Dependencies

The file depends on serialization headers, `Random`, `StringTk`, and `Locking.h`. It has no persistence of its own, but these structures are serialized as part of file inode lock state.

## Integration Points

`FileInode::LockState` serializes `EntryLockDetails` and `RangeLockDetails` collections. Unit tests use random initialization to validate serialization/deserialization paths.

## Risks and Test Signals

Equality must stay aligned with serialized fields. If new fields are added to lock detail structs, both serialization and equality/test initialization need updates. Tests should assert round-trip equality for entry and range locks and include edge ranges and empty ack IDs in addition to random values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/Locking.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/Locking.h -->
# sources/distributed-fs/beegfs/meta/source/storage/Locking.h

## Purpose

`Locking.h` defines the data structures used by `FileInode` to implement append locks, whole-file flock locks, and byte-range locks. It encodes request identity, conflict semantics, waiter queue containers, range overlap logic, and ordering comparators for current lock sets.

## Important APIs and Types

`LockEntryNotifyType` identifies append versus flock notifications. `RangeOverlapType` classifies range relationships. `EntryLockDetails` identifies whole-file locks by client node ID and client FD, includes owner PID and ack ID, serializes all fields, exposes type predicates, converts lock type to unlock, compares handles, formats diagnostic strings, and orders map/set entries by FD then client ID.

`EntryLockQueuesContainer` bundles pointers to current exclusive lock, current shared locks, exclusive/shared waiter queues, duplicate waiter ack IDs, and notify type. `AppendLockQueuesContainer` specializes it for append locks with dummy shared queues.

`RangeLockDetails` identifies range locks by client node ID and owner PID, includes ack ID, type flags, inclusive start/end offsets, and exposes handle equality, mergeability, overlap classification, trimming, splitting, merging, string formatting, and two comparators. Shared range locks are ordered by owner/client/start; exclusive range locks are ordered by start under the invariant that exclusive locks do not overlap.

## Control Flow and State

These structures are mostly value types consumed by `FileInode` lock queues. Entry locks intentionally use FD-level identity so one process can block itself through different file descriptors. Range locks intentionally use process-level identity so a process does not block itself through different descriptors. Waiter duplicate suppression is done by lock ack ID sets.

## Persistence and Dependencies

All lock detail types have serializer functions and are serialized through `FileInode::LockState`. The header depends on common lock flag definitions, node IDs, and standard containers.

## Integration Points

`FileInode` owns sets/lists of these structures and calls conflict/unlock/try-next-waiter algorithms against them. `LockingNotifier` consumes notify lists generated from successful waiter promotion.

## Risks and Test Signals

Range arithmetic uses inclusive ends and `+1` in mergeability, so max-uint64 ranges can overflow if not guarded by callers. The exclusive comparator only orders by start and relies on no overlaps, making conflict checks critical. Tests should cover entry handle equality, range overlap classes, trim/split/merge boundaries, duplicate ack IDs, NOWAIT behavior, and serialization round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/Locking.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaFileHandle.h -->
# sources/distributed-fs/beegfs/meta/source/storage/MetaFileHandle.h

## Purpose

`MetaFileHandle.h` declares a move-only handle that carries a referenced `FileInode*` plus, when needed, the parent `DirInode*` whose per-directory file store owns that inode. It lets `MetaStore` return file references without losing the directory lifetime dependency.

## Important APIs and Types

`MetaFileHandle` has a default null state, a constructor from inode and parent pointers, deleted copy operations, move construction/assignment through `swap`, pointer-like `operator->`, dereference, `get`, and a safe-bool conversion.

## Control Flow and State

The class does not release resources in its destructor. It is a transport handle, and `MetaStore::releaseFile` or close paths must be called explicitly. The parent pointer is private and friend-only because only `MetaStore` understands whether a file came from the global store or a per-directory store.

## Persistence and Dependencies

The header includes `DirInode` and `FileInode`. It owns no persistent state and performs no disk I/O.

## Integration Points

`MetaStore` returns `MetaFileHandleRes` from reference APIs and uses `MetaFileHandle` in open, close, stat-like, rename, unlink, hardlink, fsck, and reinline/deinline flows. The handle ensures parent directory references are carried alongside inodes loaded from a `DirInode::fileStore`.

## Risks and Test Signals

The main risk is misuse: the handle is not RAII, so leaks or double releases are possible if callers do not follow `MetaStore` release conventions. Tests should cover move behavior, boolean conversion, null handles, and paired release paths for global versus per-directory file stores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaFileHandle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaStore.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/MetaStore.cpp

## Purpose

`MetaStore.cpp` implements the main metadata-server façade for POSIX-like operations on BeeGFS metadata: reference/release, open/close, stat, setattr, create, unlink, hardlink, inode deinline/reinline, fsck enumeration, raw metadata resync, and file state updates. It coordinates `InodeDirStore`, global and per-directory `InodeFileStore` instances, disposal directories, global inode locks, and on-disk metadata formats.

## Important APIs and Functions

Reference APIs include `referenceDir`, `releaseDir`, `referenceFile`, `referenceFileUnlocked`, `referenceLoadedFile`, `tryReferenceFileWriteLocked`, `releaseFile`, and `referenceInode`. Open/close APIs include `openFile`, `tryOpenFileWriteLocked`, and `closeFile`. Metadata operations include `stat`, `setAttr`, `incDecLinkCount`, `setDirParent`, `mkMetaFileUnlocked`, `mkNewMetaFile`, `makeDirInode`, and `removeDirInode`.

Unlink and disposal flows include `fsckUnlinkFileInode`, `unlinkInode`, `unlinkFile`, `unlinkFileInode`, `unlinkDirEntryWithInlinedInodeUnlocked`, `unlinkDentryAndInodeUnlocked`, `unlinkInodeLater`, and `insertDisposableFile`. Repair and hardlink APIs include `linkInSameDir`, `makeNewHardlink`, `verifyAndMoveFileInode`, `deinlineFileInode`, `reinlineFileInode`, and `checkAndRepairDupFileInode`. Fsck/resync paths include `getAllInodesIncremental`, `getAllEntryIDFilesIncremental`, `getRawMetadata`, `beginResyncFor`, and `unlinkRawMetadata`. `setFileState` integrates file-state changes with `GlobalInodeLockStore`.

## Control Flow and State

`MetaStore` uses its `rwlock` mostly as a shared/exclusive operation lock. File references first try the global file store, then fall back to a parent directory and its file store. Non-inlined file inodes should live in the global store; when stale client `EntryInfo` claims an inode is inlined but on-disk metadata shows otherwise, reference/open paths release the per-directory reference and retry under a write lock after moving the referencer to the global store.

`openFile` optionally checks disposal first for session restore, then follows global, non-inlined, or per-directory paths. `closeFile` writes dynamic metadata, releases file references, and maintains parent directory references for inlined/per-directory inodes. Creation builds an inlined dentry with `FileInodeStoreData`, applies default ACLs, inherits buddy mirroring, and optionally persists remote storage targets after referencing the new inode.

Unlink flows first remove dentries, then handle inode link count and busy state. Busy last-link files are moved or linked into disposal so storage chunks can be cleaned after close. Hardlink creation de-inlines inodes first, moves references to the global store, increments link count only when the inode is not a disposal inode, and returns the updated count. Deinline writes a non-inlined inode, copies RSTs and user xattrs, then updates the dentry; reinline copies inode data back into the dentry, restores the dentry-by-entryID hard link, and removes the standalone inode.

`setFileState` inserts the inode into `GlobalInodeLockStore` with `FILE_STATE_UPDATE`, references the inode with lock-store checks bypassed, validates active sessions in `FileInode::setFileState`, persists the state, and releases resources in reverse order.

## Persistence and Dependencies

The implementation delegates durable storage to `DirInode`, `DirEntry`, `FileInode`, `FileInodeStoreData`, `MetaStorageTk`, `StorageTkEx`, xattr/file-content APIs, and POSIX directory iteration. It uses `Program` for config, local node IDs, buddy group IDs, disposal directories, metadata paths, and ACL settings. Raw resync honors the xattr-versus-file-content storage mode.

## Integration Points

This file is the integration hub for metadata network message handlers and jobs. `MsgHelperStat`, `MsgHelperMkFile`, and xattr helpers feed operations here. Fsck consumes incremental inode enumeration. Buddy resync uses raw metadata helpers and `IncompleteInode`. Chunk balancing and HSM/file-state workflows coordinate through `GlobalInodeLockStore`.

## Risks and Test Signals

Risk is high because this code encodes lock ordering, lifetime ownership, and recovery from failed operations. Comments identify races involving stale inline flags, rename versus hardlink, disposal link count underflow, and deleting active inodes. Tests should exercise global/per-directory migration, open/close with stale inline flags, disposal cleanup for open files, hardlink deinline with concurrent rename mismatch, deinline rollback after xattr/RST failure, reinline duplicate cleanup, fsck enumeration for mirrored/non-mirrored paths, raw metadata in both xattr and content modes, and file-state lock release on every error path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaStore.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaStore.h -->
# sources/distributed-fs/beegfs/meta/source/storage/MetaStore.h

## Purpose

`MetaStore.h` declares the main metadata-server object used by client-side POSIX metadata message handlers. It exposes directory and file lifecycle operations, namespace mutation, stat/setattr, fsck scanning, raw metadata access, hardlink and inode movement helpers, and the global inode lock store.

## Important APIs and Types

`MetaFileHandleRes` returns a `MetaFileHandle` and `FhgfsOpsErr`. Public methods include reference/release for dirs and files, open/close, stat, setattr, link count updates, directory parent updates, file creation, directory inode creation/removal, unlink, same-dir and remote rename helpers, fsck enumeration, reference/cache stats, disposable file insertion, entry-data extraction, hardlink creation, inode deinline/reinline verification, duplicate inode repair, raw metadata get/begin/unlink for resync, `setFileState`, and mirrored-dir invalidation.

Private state consists of `InodeDirStore dirStore`, global `InodeFileStore fileStore`, `GlobalInodeLockStore inodeLockStore`, and `RWLock rwlock`. Private helpers implement unlink variants, reference variants, global-store migration, rename overwrite checks, attr/link-count internals, deinline/reinline internals, and inode movement.

## Control Flow and State

The class intentionally centralizes lock ordering across metadata operations. Public methods acquire `rwlock` and delegate to unlocked variants when caller already holds the correct locks. File inodes may come from the global store or a parent directory store, which is why references are returned as `MetaFileHandle`.

## Persistence and Dependencies

The header depends on fsck structures, stripe patterns, remote targets, metadata errors, `EntryInfo`, locks, atomics, `FsckTk`, `GlobalInodeLockStore`, `IncompleteInode`, `MkFileDetails`, `EntryLock`, `DirEntry`, `InodeDirStore`, `InodeFileStore`, `MetadataEx`, and `MetaFileHandle`. It is not a storage format itself, but declares all operations that mutate the metadata tree.

## Integration Points

Message handlers and background jobs call `MetaStore` rather than manipulating stores directly. The global lock store is exposed through `getInodeLockStore` for internal operations such as chunk balancing and file-state updates.

## Risks and Test Signals

Any new method must preserve lock ordering between `MetaStore`, `InodeDirStore`, `DirInode`, and file stores. APIs returning `MetaFileHandle` require explicit release. Tests should focus on public operation contracts, error propagation, lock-store interaction, buddy mirroring behavior, and source-tree transitions between inlined and non-inlined file metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaStore.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaStoreRename.cpp -->
# sources/distributed-fs/beegfs/meta/source/storage/MetaStoreRename.cpp

## Purpose

`MetaStoreRename.cpp` implements the rename-related methods of `MetaStore`, including same-directory rename, overwrite validation and cleanup, remote rename insertion, source serialization, and source completion. It handles both inlined and non-inlined file inodes and coordinates dentry updates with later inode disposal.

## Important APIs and Functions

`renameInSameDir` locks the meta store and parent directory, performs the dentry rename, updates ctime, and unlinks overwritten entries after lock release if needed. `performRenameEntryInSameDir` loads and validates the source, references inlined file inodes when necessary, checks overwrite legality, and calls `DirInode::renameDirEntryUnlocked`. `checkRenameOverwrite` enforces POSIX-like no-op for same inode and rejects directory overwrites. `unlinkOverwrittenEntry` and `unlinkOverwrittenEntryUnlocked` reuse normal unlink helpers.

Remote rename support includes `moveRemoteFileInsert`, which deserializes the source inode or dentry into the destination directory, handles overwrite name removal, fixes buddy mirror flags, restores RST info, and unlinks overwritten inlined entries. `moveRemoteFileBegin` serializes either an inlined inode through the appropriate `InodeFileStore` or a non-inlined dentry. `moveRemoteFileComplete` deletes the source inode object from the global or per-directory store.

## Control Flow and State

Same-directory rename first renames the dentry and only then cleans up an overwritten inode. For overwritten busy files, cleanup can return `INUSE`; the code releases locks and calls `unlinkInodeLater`, falling back to direct unlink if the busy reference disappeared. The source file is referenced only for inlined non-directory files, because non-inlined inodes may live on another metadata server.

Remote insert removes the destination name dentry first but keeps the ID dentry for potential recovery. It creates a new `FileInode`, deserializes metadata, adjusts buddy mirror state from the destination parent, deserializes RST data if present, and calls `mkMetaFileUnlocked`.

## Persistence and Dependencies

The implementation persists through `DirInode` dentry operations, `FileInode` serialization, `MetaStore::mkMetaFileUnlocked`, and unlink helpers. It depends on raid/stripe headers, stat/mkfile helpers, `Program`, and Boost lexical casts for logging.

## Integration Points

Network rename handlers call these methods for local same-dir and cross-server rename phases. `InodeFileStore::moveRemoteBegin` and `moveRemoteComplete` provide source-side inode serialization/deletion. `MetaStore` unlink/disposal logic handles overwritten files.

## Risks and Test Signals

Risks include partial overwrite recovery, stale inlined state, remote servers with different serialization versions, RST preservation, and lock release before `unlinkInodeLater`. Tests should cover same-inode rename no-op, file-over-file overwrite, directory overwrite rejection, busy overwritten file disposal, remote insert with existing target, RST round trip, buddy mirrored destination correction, non-inlined source dentry serialization, and failed remote completion cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/storage/MetaStoreRename.cpp -->
