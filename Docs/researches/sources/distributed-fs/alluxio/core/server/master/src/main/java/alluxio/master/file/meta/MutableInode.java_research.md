# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/MutableInode.java

## Purpose
`MutableInode` is the abstract base for mutable file and directory inodes in the file master. It stores shared metadata and implements the `InodeView` read contract plus mutation helpers for ACLs, timestamps, TTL, persistence, pinning, xattrs, ownership, and proto conversion.

## Important APIs, Types, and Functions
Important methods include shared getters, ACL mutation (`setAcl`, `replaceAcl`, `removeAcl`, `removeExtendedAcl`, `updateMask`, `setInternalAcl`), timestamp setters with optional override, owner/group/mode setters, `setPersistenceState()`, `setPinned()`, `setXAttr()` with strategies `TRUNCATE`, `UNION_REPLACE`, `UNION_PRESERVE`, and `DELETE_KEYS`, `updateFromEntry(UpdateInodeEntry)`, type casts `asDirectory()`/`asFile()`, permission checks, and `toProtoBuilder()`. Subclasses implement `setDefaultACL()`, `generateClientFileInfo()`, `getThis()`, and `toJournalEntry(String)`.

## Control Flow, State, and Persistence
Each inode carries id, name, parent id, creation/modification/access times, deletion flag, directory flag, TTL and action, persistence state, pinned flag, pinned media set, ACL, UFS fingerprint, and xattrs. `updateFromEntry()` is the central replay/update method for common fields; it interns owner/group strings, respects timestamp overwrite flags, applies xattr update strategies, and filters pinned medium types against configured global media. `toProtoBuilder()` serializes common inode fields to metastore proto; journal serialization is completed by subclasses.

## Dependencies and Integration Points
`MutableInodeDirectory` and `MutableInodeFile` extend this base. `InodeTreePersistentState` obtains mutable inodes from `InodeStore`, applies journal entries through `updateFromEntry()`, and writes them back. ACL behavior depends on Alluxio security authorization classes and proto conversion utilities. Configuration provides allowed tiered-store medium types.

## Risks
The class is not thread-safe; only timestamp setters synchronize locally, and higher-level inode locks are required. `setXAttr()` can retain and mutate caller-provided maps instead of copying them. File subclasses throw for default ACL operations, so common ACL code must not pass default entries to files unless expected. Equality and hash code use only inode id, which is correct for identity but can hide stale object comparisons.

## Test Signals
Tests should cover ACL replace/modify/remove/default behavior, mask recomputation, timestamp monotonic and override semantics, xattr update strategies, pin medium filtering, `UpdateInodeEntry` field application, proto round trips through subclasses, and file/directory cast failures.
