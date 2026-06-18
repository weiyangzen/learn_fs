<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.h -->
## sources/distributed-fs/beegfs/common/source/common/components/StreamListener.h

### Purpose
This header declares the stream listener thread responsible for TCP/RDMA accept and incoming stream socket dispatch.

### Important APIs, Types, And Functions
`StreamListener` exposes constructor/destructor, `getSockReturnFD`, and `getWorkQueue`. Private methods cover socket/pipe initialization, the run loop, incoming connection/data handlers, socket return handling, RDMA idle checks, socket option application, false alarm checks, and cleanup.

### Control Flow
As a `PThread`, the listener owns its event loop internally. External workers interact by writing returned socket pointers to `getSockReturnFD()`.

### State, Persistence, And Dependencies
State includes log context, TCP/RDMA listen sockets, `MultiWorkQueue`, epoll fd, `PollList`, `Pipe`, and RDMA idle-check counters. Dependencies include logging, work queues, component exceptions, socket classes, net messages, nodes, threading, poll utilities, and `Common`.

### Integration Points
Used by BeeGFS services to accept stream connections and dispatch `IncomingDataWork`. It bridges low-level sockets and worker queues.

### Risks
Raw pointer ownership is central and not encoded in types. Public return-pipe fd exposes a low-level protocol: writers must send exact `Socket*` values back.

### Test Signals
Tests should validate construction/destruction ownership, worker return protocol, TCP-only and RDMA-capable startup, and poll list consistency as sockets move between listener and workers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/components/StreamListener.h -->
