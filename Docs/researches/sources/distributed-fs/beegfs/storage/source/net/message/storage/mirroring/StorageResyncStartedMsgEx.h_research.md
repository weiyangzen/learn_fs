<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h

### Purpose
Declares the handler for storage-resync-started notifications and its session cleanup helper.

### Important APIs, Types, And Functions
StorageResyncStartedMsgEx derives from StorageResyncStartedMsg, overrides processIncoming(ResponseContext&), and declares private deleteMirrorSessions(uint16_t).

### Control Flow
The helper split makes the side effect explicit: handling the message is primarily a session-store cleanup operation.

### State, Persistence, And Dependencies
No local state is declared. Depends on StorageResyncStartedMsg and session classes in the implementation.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Risk is that cleanup policy is hidden behind a private helper with no return status, so failures cannot be surfaced in the response.

### Test Signals
Tests should validate deletion behavior via the cpp handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/mirroring/StorageResyncStartedMsgEx.h -->
