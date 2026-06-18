## sources/distributed-fs/beegfs/storage/source/net/message/fsck/MoveChunkFileMsgEx.cpp

### Purpose
`MoveChunkFileMsgEx.cpp` handles fsck-triggered relocation of a chunk file within a storage target's chunk tree. It can operate on normal or mirrored chunk directories and optionally prevents overwriting an existing destination.

### Important APIs, Types, And Functions
`processIncoming()` responds with `MoveChunkFileRespMsg(moveChunk())`. `moveChunk()` reads chunk name, old/new paths, target ID, overwrite flag, and mirror flag; resolves the target; checks destination existence when overwrite is disabled; creates the destination parent directory with `StorageTk::createPathOnDisk()`; and calls `renameat()` between target-relative paths.

### Control Flow, State, And Persistence
The operation returns `0` on success and `1` on failure. On mirrored moves, success marks the target as needing buddy resync via `setBuddyNeedsResync(true)`. Persistent effects are directory creation and the actual chunk rename.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on target FDs, `StorageTk`, `Path`, and fsck messages. Risks include broad `Log_CRITICAL` logging for request errors, races between destination existence check and rename, path trust from fsck, and mirror resync side effects. Tests should cover unknown target, overwrite false with existing destination, parent creation failure, normal rename, mirrored rename, and `renameat()` failures.
