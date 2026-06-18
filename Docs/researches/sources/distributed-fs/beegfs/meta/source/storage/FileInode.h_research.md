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
