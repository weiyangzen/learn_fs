## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/GetChunkFileAttribsMsgEx.cpp

### Purpose
`GetChunkFileAttribsMsgEx.cpp` handles requests for dynamic attributes of a chunk file: size, allocated blocks, modification/access times, and storage version.

### Important APIs, Types, And Functions
`processIncoming()` resolves mirror buddy group targets, handles unknown targets, validates mirrored target consistency with `getTargetFD()`, builds the chunk path with `StorageTk::getFileChunkPath()`, locks the path through `SyncedStoragePaths::lockPath()`, calls `fstatat()`, and replies with `GetChunkFileAttribsRespMsg`. `getTargetFD()` chooses normal or mirror FD and can send `GenericResponseMsg` for non-good mirrored primaries.

### Control Flow, State, And Persistence
The handler is read-only except for path storage-version locking and op stats. Missing files are not treated as errors; the response has zero storage version, so metadata should avoid updating from absent data.

### Dependencies, Integration Points, Risks, And Test Signals
It depends on storage targets, mirror mappers, target consistency state, synchronized storage paths, `StorageTk`, and op stats. Risks include response suppression after `GenericResponseMsg`, correctness of storage version with concurrent truncation/write, and non-error missing-file semantics. Tests should cover existing file, missing file, unknown normal target, unknown mirror target, non-good mirror primary, secondary flag, stat errors, and storage version locking.
