# sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h -->
## sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h

### Purpose
`sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h` contains BeeGFS common code for `IncomingPreprocessedMsgWork`. More broadly, it participates in the V2 stream listener pipeline for accepting sockets, preprocessing message headers, dispatching worker jobs, and returning sockets to epoll.

### Important APIs, Types, And Functions
Detected classes: [('IncomingPreprocessedMsgWork', 'Work'), ('is', '')]. Detected functions: []. Detected classes are [('IncomingPreprocessedMsgWork', 'Work'), ('is', '')]; structs none; enums none; notable out-of-line methods none.

### Control Flow
Control flow follows the functions listed above.

### State, Persistence, And Dependencies
Includes/dependencies visible in this file include `common/app/AbstractApp.h`, `common/components/worker/Work.h`, `common/net/message/NetMessage.h`, `common/net/sock/Socket.h`, `common/Common.h`. Important local state or payload members include `AbstractApp* app`, `Socket* sock`, `NetMessageHeader msgHeader`. State is process-local unless it is serialized into BeeGFS network messages or reflected in socket/worker side effects.

### Integration Points
This source-tree-aligned file integrates with adjacent BeeGFS common components through the types, includes, queues, sockets, or NETMSGTYPE constants named above. Message and fsck types are consumed by app-specific message factories and request handlers; worker/listener types are driven by PThread components and MultiWorkQueue.

### Risks
Primary risks include socket ownership, epoll/pipe rearming, timeout, disconnect, and RDMA immediate-data paths. Changes should preserve the wire format, ownership model, and queue/socket lifecycle implied by the current implementation.

### Test Signals
Useful test signals include success, invalid input, and error/exception paths through process methods, enqueue/dequeue ordering, worker deletion, stats/counter updates, and shutdown behavior, socket timeout, disconnect, oversized message, and authentication/direct-channel cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/streamlistenerv2/IncomingPreprocessedMsgWork.h -->
