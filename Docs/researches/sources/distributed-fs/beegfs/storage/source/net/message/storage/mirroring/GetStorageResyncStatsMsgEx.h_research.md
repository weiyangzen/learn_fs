<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.h

### Purpose
Declares the storage-side handler for querying resync job statistics.

### Important APIs, Types, And Functions
The class derives from GetStorageResyncStatsMsg and overrides processIncoming(ResponseContext&).

### Control Flow
The header exposes only the message-dispatch entry point; target/job lookup is in the cpp file.

### State, Persistence, And Dependencies
No handler-local state exists. Depends on common GetStorageResyncStatsMsg and StorageErrors headers.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is minimal and limited to dispatch signature drift.

### Test Signals
A compile-time message factory test covers this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/GetStorageResyncStatsMsgEx.h -->
