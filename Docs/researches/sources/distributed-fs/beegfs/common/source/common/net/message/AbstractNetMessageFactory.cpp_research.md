# sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp -->
## sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp` implements common NetMessage deserialization and validation before dispatching payloads to concrete message classes. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
createFromRaw() checks NETMSG_MIN_LENGTH, deserializes NetMessageHeader, and delegates to createFromPreprocessedBuf(). createFromPreprocessedBuf() calls virtual createFromMsgType(), applies feature flags, rejects unsupported feature flags, validates generic header flags against supportsMirroring(), copies the header into the message, and calls deserializePayload(). Failures return SimpleMsg(NETMSGTYPE_Invalid). Detected classes are none; structs none; enums none; notable out-of-line methods ['AbstractNetMessageFactory::createFromPreprocessedBuf()', 'AbstractNetMessageFactory::createFromRaw()'].

### Control Flow
No state is retained. Dependencies include NetMessage, SimpleMsg, NetMessageLogHelper, LogContext, StringTk, and serialization. Integration is central to stream workers, LocalConnWorker, and MessagingTk response parsing.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/log/LogContext.h`, `common/net/message/NetMessageLogHelper.h`, `AbstractNetMessageFactory.h`, `SimpleMsg.h`. Important local state or payload members include `NetMessageHeader header`, `return msg`, `return msg`. Protocol persistence depends on stable message IDs: `NETMSGTYPE_Invalid`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include borrowed pointer lifetime and deserialized buffer backing, message factory coverage and wire-format compatibility. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include serialization/deserialization round trips, including empty and multi-item payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.cpp -->
