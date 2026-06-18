<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.h -->
## sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.h

### Purpose
Declares the storage extension for SetLocalAttrMsg and the private helpers used to resolve target file descriptors and forward mirrored attribute changes.

### Important APIs, Types, And Functions
The class derives from SetLocalAttrMsg and overrides processIncoming(ResponseContext&). Private helpers getTargetFD(const StorageTarget&, ResponseContext&, bool*) and forwardToSecondary(StorageTarget&, ResponseContext&, bool*) encode the implementation contract used by the source file.

### Control Flow
The header establishes that all message handling enters through processIncoming, while target-state validation and buddy forwarding are isolated in helpers so the body can keep local POSIX attribute updates separate from communication policy.

### State, Persistence, And Dependencies
No state is declared here; state is inherited from the serialized SetLocalAttrMsg and accessed via base-class getters during processing. Depends on common StorageErrors, SetLocalAttrMsg, ResponseContext via included base declarations, and the forward-declared StorageTarget.

### Integration Points
This file integrates with the surrounding BeeGFS storage daemon or Linux kernel documentation/build tree through the dependencies and message/schema contracts described above. Its callers should treat the documented response formats, filesystem effects, and validation rules as the stable integration surface.

### Risks
Interface risk is that helper return conventions are non-obvious: getTargetFD can send a response itself via outResponseSent, while forwardToSecondary can also send GenericResponseMsg and return COMMUNICATION.

### Test Signals
Compile and message-dispatch tests should verify the class remains registered as the concrete handler for NETMSGTYPE_SetLocalAttr and that helper declarations stay synchronized with the cpp file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/storage/source/net/message/storage/attribs/SetLocalAttrMsgEx.h -->
