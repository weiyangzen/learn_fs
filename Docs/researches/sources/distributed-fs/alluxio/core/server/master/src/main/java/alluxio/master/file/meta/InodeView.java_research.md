# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/InodeView.java

## Purpose
`InodeView` defines the read-only inode contract shared by mutable inodes and immutable/wrapped inode views. It gives callers a stable interface for common metadata, permissions, client `FileInfo` generation, proto conversion, and journal representation without requiring mutation access.

## Important APIs, Types, and Functions
The interface exposes timestamps, owner/group/mode, id/name/parent id, TTL and TTL action, persistence state, deleted/file/directory/pinned/persisted flags, pinned medium types, UFS fingerprint, xattrs, access/default ACLs, permission checks, `generateClientFileInfo(String)`, and `toProto()`. It extends `JournalEntryRepresentable` and `Comparable<InodeView>`, comparing by inode name.

## Control Flow, State, and Persistence
There is no implementation state. Persistence behavior is indirect: implementers must serialize themselves to journal entries through `JournalEntryRepresentable` and to metastore proto through `toProto()`. Permission checks are delegated by implementations to their `AccessControlList`.

## Dependencies and Integration Points
The interface is consumed by lock managers, path logic, metadata listing, permission checks, metastore serialization, and client response construction. `MutableInode`, `MutableInodeDirectory`, and `MutableInodeFile` implement this contract, while `InodeTree`, `InodeLockManager`, and `LockedInodePath` accept `InodeView` where mutation is not required.

## Risks
The default `compareTo()` sorts only by name, so two inodes with the same name under different parents compare equal. Callers should not use it as a global identity ordering. Returning mutable structures such as xattr maps or ACL objects depends on implementation discipline; the interface itself does not enforce deep immutability.

## Test Signals
Contract tests should verify file and directory implementations provide consistent `FileInfo`, proto, and journal fields; permission checks match ACL behavior; and compare-by-name ordering is acceptable for local child-list use but not used as a global unique key.
