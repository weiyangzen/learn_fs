# sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h` defines NetMessage infrastructure or simple payload base `NetMessageTypes`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('NetMsgStrMapping', '')]. Message type coverage: NETMSGTYPE_Ack, NETMSGTYPE_AckNotify, NETMSGTYPE_AckNotifyResp, NETMSGTYPE_AddStoragePool, NETMSGTYPE_AddStoragePoolResp, NETMSGTYPE_AdjustChunkPermissions, NETMSGTYPE_AdjustChunkPermissionsResp, NETMSGTYPE_AuthenticateChannel, NETMSGTYPE_BumpFileVersion, NETMSGTYPE_BumpFileVersionResp, NETMSGTYPE_ChangeTargetConsistencyStates, NETMSGTYPE_ChangeTargetConsistencyStatesResp.... Serialization fields detected: handled by derived classes or switch tables. Detected classes are [('NetMsgStrMapping', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Protocol persistence depends on stable message IDs: `NETMSGTYPE_Ack`, `NETMSGTYPE_AckNotify`, `NETMSGTYPE_AckNotifyResp`, `NETMSGTYPE_AddStoragePool`, `NETMSGTYPE_AddStoragePoolResp`, `NETMSGTYPE_AdjustChunkPermissions`, `NETMSGTYPE_AdjustChunkPermissionsResp`, `NETMSGTYPE_AuthenticateChannel`, ... State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessageTypes.h -->
