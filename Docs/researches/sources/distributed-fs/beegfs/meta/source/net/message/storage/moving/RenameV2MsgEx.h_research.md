<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.h -->
# sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.h

## Purpose
Declares the mirrored rename message and its composite lock set.

## Important APIs, Types, and Functions
`RenameV2Locks` owns the destination-file hash lock, source/destination name locks, source/destination directory locks, source file locks for file and directory cases, and overwritten-file lock. It is move-only and supports `swap()`. `RenameV2MsgEx` inherits `MirroredMessage<RenameMsg, RenameV2Locks>`, overrides processing, locking, execution, mirror status, forwarding, and secondary response handling. Private helpers split same-dir rename, directory rename, file rename, remote insert/unlink, directory parent update, remote inode unlink, and link-count lookup.

## Control Flow, State, and Persistence
The header makes rename a single mirrored state-changing operation with many possible sub-operations. `isMirrored()` uses the source directory mirror flag, so the initiating source side governs mirrored replay.

## Dependencies and Integration Points
Includes rename request/response messages, `MirroredMessage`, `DirEntry`, and `MetaStore`. It coordinates with moving and creating message helpers declared elsewhere.

## Risks and Test Signals
The lock struct is central to deadlock avoidance. Tests should verify move-only behavior compiles, lock acquisition ordering for same/different dirs and same/different inode IDs, and secondary response error mapping from `RenameRespMsg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/message/storage/moving/RenameV2MsgEx.h -->
