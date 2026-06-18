<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.cpp

## Purpose
Provides shared unlink helpers for metadata dentries, file inodes, storage chunks, and disposal fallback.

## Important APIs, Types, and Functions
`unlinkFile()` wraps `unlinkMetaFile()` and `unlinkChunkFiles()`. `unlinkMetaFile()` calls `MetaStore::unlinkFile()` and emits `ModificationEvent_FILEREMOVED`. `unlinkFileInode()` decrements hardlink count and returns an inode when link count reaches zero. `unlinkChunkFiles()` calls `unlinkChunkFilesInternal()` and inserts the inode into the disposable store if chunk deletion fails. `unlinkChunkFileSequential()` sends `UnlinkLocalFileMsg` to each target and ignores unknown node/target errors. `unlinkChunkFileParallel()` schedules `UnlinkChunkFileWork` for each target.

## Control Flow, State, and Persistence
Metadata unlink happens first; chunk unlink is required only when an unlinked inode object is returned. Storage deletion failures do not recreate metadata; instead the inode is persisted into disposal for later retry. Modification events are emitted based on metadata unlink entry ID.

## Dependencies and Integration Points
Depends on `MetaStore`, `DirInode`, `FileInode`, `ModificationEventFlusher`, `UnlinkLocalFileMsg/RespMsg`, target mappers/states, `UnlinkChunkFileWork`, `MultiWorkQueue`, and disposal-store insertion. Used by unlink, rename overwrite cleanup, close disposal, and moving rollback.

## Risks and Test Signals
Risks include emitting removal events after failed unlink if `entryInfo` is stale, suppressing unknown target errors, disposal insertion failure after chunk delete failure, and partial parallel unlink. Tests should cover open-file disposal, hardlink decrement, inlined/non-inlined inode cleanup, sequential/parallel storage deletion, unknown target suppression, disposal fallback, and modification-event conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperUnlink.cpp -->
