# sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h -->
## sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h` defines NetMessage infrastructure or simple payload base `AbstractNetMessageFactory`. More broadly, it defines core NetMessage infrastructure or simple message payload base classes.

### Important APIs, Types, And Functions
Important APIs/classes detected: [('AbstractNetMessageFactory', '')]. Message type coverage: core message infrastructure, not a single message type. Serialization fields detected: handled by derived classes or switch tables. Detected classes are [('AbstractNetMessageFactory', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow is CRTP serialization/deserialization, message type lookup, response sending, or simple payload storage depending on the file.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/net/message/NetMessage.h`. Important local state or payload members include `return result`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include compile coverage, boundary values, and caller lifetime assumptions. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include compile-time inclusion and boundary-value checks for public APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/message/AbstractNetMessageFactory.h -->
