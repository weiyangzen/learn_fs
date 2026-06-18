<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.h -->
## sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.h

### Purpose
This header declares the abstract UDP datagram listener base used by BeeGFS components that receive and send datagram messages.

### Important APIs, Types, And Functions
It defines UDP buffer sizes, `StandardSocketMap`, public send helpers, ack send helpers, `sendDummyToSelfUDP`, `sendto` wrappers, receive timeout setter, UDP port getter, and `setLocalNicList`. Subclasses must implement `handleIncomingMsg`.

### Control Flow
The class derives from `PThread`; `run` and `listenLoop` are private base behavior, while subclass control is limited to handling already parsed incoming messages.

### State, Persistence, And Dependencies
The class stores sockets, interface maps, routing/source cache, buffers, ack store, net filter, local NICs, and synchronization state. Dependencies include logging, atomics, threading, standard sockets, acknowledgeable messages, node stores, and component exceptions.

### Integration Points
Registration and service-specific datagram listeners inherit this base. Friend work classes can access send mutex for efficient notification batching.

### Risks
The public inline `sendto` overloads expose the unusual `ENETUNREACH`/`EAFNOSUPPORT` positive return behavior. Buffer pointers are raw and initialized after thread start, so message handlers rely on `run` calling `initBuffers` first.

### Test Signals
Compile tests should ensure derived classes implement `handleIncomingMsg`. Runtime tests should validate send path selection, mutex behavior, receive timeout updates, and self-wakeup through `sendDummyToSelfUDP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/AbstractDatagramListener.h -->
