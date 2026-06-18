<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h

### Purpose
Declares the storage extension for the chunk-balancer statistics request.

### Important APIs, Types, And Functions
The class derives from GetChunkBalanceJobStatsMsg and only overrides processIncoming(ResponseContext&).

### Control Flow
All control flow is delegated to the cpp implementation; the header exposes no helper API or state.

### State, Persistence, And Dependencies
No persistent or runtime state is held in this class beyond inherited message fields. Depends on common GetChunkBalanceJobStatsMsg and StorageErrors headers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is minimal, mostly dispatch drift if the base message or response type changes.

### Test Signals
A compile-time dispatch test is sufficient for the header; behavior tests live with the cpp handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/GetChunkBalanceJobStatsMsgEx.h -->
