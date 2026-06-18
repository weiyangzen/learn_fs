<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.h

### Purpose
Declares the storage-side CpChunkPaths handler that accepts chunk balance copy candidates and owns lazy job startup.

### Important APIs, Types, And Functions
CpChunkPathsMsgEx derives from CpChunkPathsMsg, overrides processIncoming(ResponseContext&), and declares private addChunkBalanceJob(bool&).

### Control Flow
The header separates network-message dispatch from job lifecycle creation; all detailed target resolution and enqueue behavior is in the implementation.

### State, Persistence, And Dependencies
No member state is stored on the handler. Runtime state is held by the App singleton ChunkBalancerJob pointer. Depends on the common CpChunkPathsMsg base class and ChunkBalancerJob declaration.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is lifetime coupling: addChunkBalanceJob returns a raw pointer owned by App, so ownership must remain documented in the cpp path.

### Test Signals
Build tests should cover inclusion from message factories and ensure the override signature matches NetMessage dispatch expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/chunkbalancing/CpChunkPathsMsgEx.h -->
