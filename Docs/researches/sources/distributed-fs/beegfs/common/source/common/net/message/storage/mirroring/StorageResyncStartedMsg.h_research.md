<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedMsg.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedMsg.h

### Purpose
`StorageResyncStartedMsg` notifies another component that storage resync has started for a buddy target.

### Important APIs, Types, And Functions
It subclasses `SimpleUInt16Msg` with type `NETMSGTYPE_StorageResyncStarted`; the payload is the buddy target ID.

### Control Flow
Senders construct with a `buddyTargetID`; receivers read the inherited uint16 payload.

### State, Persistence, And Dependencies
The message is transient notification state. It depends on `SimpleUInt16Msg`.

### Integration Points
Storage resync coordination and management state machines use it to synchronize resync lifecycle transitions.

### Risks
The class does not provide a named getter, so callers use inherited `getValue()` or message-specific handling. Tests should cover target-ID round-trip and paired acknowledgement behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/storage/mirroring/StorageResyncStartedMsg.h -->
