# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/Inode.java

Purpose: read-only wrapper base class for inode views. It delegates all common inode accessors to an underlying `InodeView` while providing convenient typed casts and wrapping logic.

Important APIs and types: implements common getters for timestamps, owner/group, id, TTL, mode, persistence state, parent id, xattrs, deleted/directory/file/pinned/persisted flags, UFS fingerprint, ACLs, medium types, client info, permissions, proto, and journal entry. `asDirectory`, `asFile`, and static `wrap` provide typed access.

Control flow: `wrap` returns existing `Inode` instances unchanged, otherwise checks `isFile` and wraps `InodeFileView` as `InodeFile` or `InodeDirectoryView` as `InodeDirectory`. `asDirectory` and `asFile` validate type before casting.

State and persistence behavior: wrapper owns no persistence but exposes `toProto` and `toJournalEntry` delegated from the underlying inode. Modifications to the delegate are visible through the wrapper, so it is read-only by interface, not immutable by snapshot.

Dependencies and integration points: depends on `InodeView`, inode file/directory views, ACL classes, journal/proto types, and client `FileInfo`. It is widely used by inode tree traversal, metadata sync, locks, and store APIs.

Risks: equality compares wrapped delegates only when the other object is also `Inode`, so equality with raw `InodeView` delegates is not symmetric. The read-only wrapper can reflect concurrent delegate mutation if underlying objects are mutable.

Test signals: tests should cover wrapping file and directory views, invalid casts, delegated values, equality/hash code, and journal/proto delegation.
