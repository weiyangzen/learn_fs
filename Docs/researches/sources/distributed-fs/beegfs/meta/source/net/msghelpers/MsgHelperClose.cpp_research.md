<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.cpp -->
# sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.cpp

## Purpose
Provides shared close-file helpers for metadata messages, coordinating session-store removal, storage target close RPCs, dynamic attribute updates, inode reference close, disposal decisions, and mirrored disposal behavior.

## Important APIs, Types, and Functions
`closeFile()` wraps `closeSessionFile()`, `closeChunkFile()`, timestamp capture, and `MetaStore::closeFile()`, returning whether a disposal file should be unlinked. `closeSessionFile()` removes a session file by owner FD, or recovers by opening metadata when the meta-server lost session state. `closeChunkFile()` chooses sequential or parallel storage close. `closeChunkFileSequential()` sends `CloseChunkFileMsg` per target and applies returned dynamic attributes. `closeChunkFileParallel()` schedules `CloseChunkFileWork` on the communication slave queue. `unlinkDisposableFile()` deletes a file from normal or mirrored disposal directories unless mirrored disposal GC is configured.

## Control Flow, State, and Persistence
Session state is removed from normal or mirrored `SessionStore`. Storage close RPCs return size/block/time dynamic attributes that are applied to the inode before the inode is closed in `MetaStore`. If hardlinks and references reach zero, callers can unlink the disposal file. Disposal unlink mutates metadata through `MsgHelperUnlink`.

## Dependencies and Integration Points
Depends on session stores, `SessionTk`, `CloseChunkFileMsg/RespMsg`, storage target mapping/state stores, `CloseChunkFileWork`, `MetaStore`, `MsgHelperUnlink`, stripe patterns, path info, and mirrored disposal configuration.

## Risks and Test Signals
Risks include session recovery opening with read/write when original flags are unknown, storage close errors after session removal, ignored `INUSE` target errors, partial dynamic attributes, and delayed mirrored disposal cleanup. Tests should cover missing session recovery, sequential and parallel close, buddy-mirror pattern close, max-used-node `-1`, dynamic attribute propagation, timestamp capture, and disposal unlink gating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/meta/source/net/msghelpers/MsgHelperClose.cpp -->
