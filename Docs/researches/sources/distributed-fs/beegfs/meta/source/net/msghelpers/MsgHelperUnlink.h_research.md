<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.h -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.h

## Purpose
Declares static unlink helpers for metadata and storage cleanup.

## Important APIs, Types, and Functions
Public methods are `unlinkFile()`, `unlinkMetaFile()`, `unlinkFileInode()`, `unlinkChunkFiles()`, and inline-public `unlinkChunkFilesInternal()`. Private methods implement sequential/parallel chunk deletion and an unused/undeclared-in-implementation `insertDisposableFile(FileInode&)` declaration.

## Control Flow, State, and Persistence
The signatures expose ownership transfer: `unlinkChunkFiles(FileInode*)` consumes and deletes or stores the raw inode pointer. `unlinkMetaFile()` may return a `unique_ptr<FileInode>` requiring caller cleanup.

## Dependencies and Integration Points
Includes `Path`, common types, and `MetaStore`. Used widely by creating, moving, close, and helper paths.

## Risks and Test Signals
Callers must respect ownership semantics to avoid leaks or double deletes. Tests should verify `unique_ptr` output behavior and that `unlinkChunkFilesInternal()` remains safe when called directly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.h -->
