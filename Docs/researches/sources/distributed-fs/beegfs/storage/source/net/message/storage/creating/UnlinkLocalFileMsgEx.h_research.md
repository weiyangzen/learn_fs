<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.h

### Purpose
Declares the storage extension for unlinking one local chunk file and its mirrored-forwarding helpers.

### Important APIs, Types, And Functions
The class derives from UnlinkLocalFileMsg, overrides processIncoming(ResponseContext&), and declares getTargetFD() plus forwardToSecondary().

### Control Flow
The helper split mirrors SetLocalAttrMsgEx and keeps target consistency checks and secondary forwarding separate from local unlink logic.

### State, Persistence, And Dependencies
No state is held in the class outside inherited message fields and temporary stack state in processIncoming. Depends on UnlinkLocalFileMsg and a forward declaration of StorageTarget.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
The outResponseSent and COMMUNICATION conventions are subtle and must match the cpp implementation to avoid double responses.

### Test Signals
Header-level test signal is dispatch compilation; behavioral coverage belongs to the cpp handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/creating/UnlinkLocalFileMsgEx.h -->
