# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInodeDirectory.java

## Purpose
`MutableInodeDirectory` is the mutable metadata representation for directories in the file master. It adds directory-specific state to `MutableInode`: mount-point status, direct-children-loaded flag, child count, and default ACL.

## Important APIs, Types, and Functions
Directory-specific APIs include `isMountPoint()`, `isDirectChildrenLoaded()`, `getChildCount()`, `getDefaultACL()`, setters for mount point/direct-children-loaded/child count/default ACL, `generateClientFileInfo()`, `updateFromEntry(UpdateInodeDirectoryEntry)`, static `fromJournalEntry()`, static `create()`, `toJournalEntry()`, `toJournalEntry(String)`, `toProto()`, and `fromProto()`.

## Control Flow, State, and Persistence
The private constructor initializes a directory inode with no mount point, no loaded direct children, zero child count, and a default ACL derived from the access ACL. `create()` builds a new directory from `CreateDirectoryContext`, including owner/group/mode, ACLs, mount flag, TTL, xattrs, and optional UFS fingerprint. `fromJournalEntry()` supports backward compatibility by building ACLs from owner/group/mode when no ACL proto is present and by using modification time as access time if the journal lacks access time. Journal and proto serialization include access/default ACLs, medium types, xattrs, direct-children-loaded, mount-point status, and child count in proto.

## Dependencies and Integration Points
`InodeTree.createPath()` creates these for root, missing parents, and target directories. `InodeTreePersistentState` applies directory creation and directory update entries, increments parent child counts, and stores directories in `InodeStore`. Mount operations and metadata loading rely on `isMountPoint()` and `isDirectChildrenLoaded()`.

## Risks
`isDirectChildrenLoaded()` and its setter are synchronized, but most other fields are not; caller locking is required. `fromJournalEntry()` initializes a missing default ACL to a new empty default ACL rather than one derived from access ACL, which preserves older journal semantics but differs from fresh construction. `generateClientFileInfo()` sets UFS fingerprint to `INVALID_UFS_FINGERPRINT` for directories even though the inode may carry a fingerprint.

## Test Signals
Tests should cover create context mapping, ACL/default ACL inheritance and serialization, journal/proto round trips, backward-compatible journal entries without ACL/access time, direct-children-loaded updates, child count in proto, and client `FileInfo` fields for directories and mount points.
