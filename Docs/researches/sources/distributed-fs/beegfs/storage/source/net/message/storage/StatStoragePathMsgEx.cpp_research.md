## sources/distributed-fs/beegfs/storage/source/net/message/storage/StatStoragePathMsgEx.cpp

### Purpose
`StatStoragePathMsgEx.cpp` handles statfs-style requests for a storage target path. It returns total/free bytes and inode counts.

### Important APIs, Types, And Functions
`processIncoming()` calls `statStoragePath()` and responds with `StatStoragePathRespMsg`, then updates `StorageOpCounter_STATSTORAGEPATH`. `statStoragePath()` resolves the target, calls `StorageTk::statStoragePath()`, applies manual free-space override through `StorageTk::statStoragePathOverride()`, and returns a BeeGFS error code.

### Control Flow, State, And Persistence
The handler is read-only except op counters. Unknown targets return `UNKNOWNTARGET`; statfs failures return `INTERNAL`. Override files can change reported free space/inodes without changing the actual filesystem.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on `StorageTargets`, `StorageTk`, response messages, and op stats. Risks include override semantics, statfs failure handling, and path lifetime from target configuration. Tests should cover valid target stats, unknown target, statfs failure, override file behavior, and op-counter updates.
