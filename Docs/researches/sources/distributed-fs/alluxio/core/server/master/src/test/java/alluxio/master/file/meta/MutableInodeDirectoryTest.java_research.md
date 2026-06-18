# sources/distributed-fs/alluxio/core/server/master/src/test/java/alluxio/master/file/meta/MutableInodeDirectoryTest.java

## Purpose
This file tests the mutable directory inode data model: identity, type flags, deleted state, timestamps, naming, parent linkage, permissions, and client-facing `FileInfo` generation.

## Important APIs, Types, and Functions
It exercises `MutableInodeDirectory.create`, `equals`, `getId`, `isDirectory`, `isFile`, `setDeleted`, timestamp getters/setters, `setName`, `setParentId`, `getMode`, and `generateClientFileInfo`.

## Control Flow, State, and Persistence
Tests create isolated directory inodes from `AbstractInodeTest`, mutate one field at a time, and assert the in-memory object state. Timestamp setters reject backwards updates by leaving the previous time intact.

## Dependencies and Integration Points
The test depends on `CreateDirectoryContext`, security umask configuration, `ModeUtils.applyDirectoryUMask`, and `alluxio.wire.FileInfo` fields consumed by clients.

## Risks
Equality is id-based rather than name-based, which is intentional but easy to misuse. The generated client info is a serialization boundary; incorrect defaults such as cacheable, folder, completed, length, or UFS path would leak to clients.

## Test Signals
Signals cover id-based equality, directory/file flags, deletion toggling, monotonic timestamp behavior, default owner/group/mode, and directory `FileInfo` shape.
