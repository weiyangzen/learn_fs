# sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h` defines BeeGFS wire message header layout, base message behavior, response context, and CRTP serialization helpers. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
NetMessageHeader stores length, feature/compat flags, generic flags, BeeGFS data-version prefix, message type, target/user IDs, and sequence fields. NetMessage serializes by writing a header, serializing payload, then fixing the length field; it also exposes feature flag, target/user, sequence, generic flag, and socket-release helpers. ResponseContext sends responses over stream or datagram sockets. NetMessageSerdes and MirroredMessageBase implement common payload patterns. Detected classes are [('NetMessage', ''), ('AbstractNetMessageFactory', ''), ('TestMsgSerializationBase', ''), ('ResponseContext', ''), ('NetMessage', ''), ('NetMessageSerdes', 'NetMessage'), ('MirroredMessageBase', 'NetMessage')]; structs ['NetMessageHeader', 'NetMessageHeader', 'sockaddr', 'sockaddr']; enums none; notable out-of-line methods none.

### Control Flow
State is per-message header, releaseSockAfterProcessing, and optional backingBuffer for vector-backed deserialization. Dependencies include Socket, NetworkInterfaceCard, Serialization, HighResolutionStats, NetMessageTypes, NetMessageLogHelper, and IPAddress.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/sock/NetworkInterfaceCard.h`, `common/net/sock/Socket.h`, `common/toolkit/HighResolutionStats.h`, `common/toolkit/serialization/Serialization.h`, `common/Common.h`, `NetMessageLogHelper.h`, `NetMessageTypes.h`, `common/net/sock/IPAddress.h`. Important local state or payload members include `uint32_t       msgLength; // in bytes`, `uint8_t        msgCompatFeatureFlags`, `uint8_t        msgFlags`, `uint16_t       msgType; // the type of payload, defined as NETMSGTYPE_x`, `uint32_t       msgUserID; // system user ID for per-user msg queues, stats etc.`, `uint64_t       msgSequence; // for retries, 0 if not present`, `uint64_t       msgSequenceDone; // a sequence number that has been fully processed, or 0`, `uint32_t length`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Invalid`, `NETMSGTYPE_x`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths, borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads, success, invalid input, and error/exception paths through process methods, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/NetMessage.h -->
