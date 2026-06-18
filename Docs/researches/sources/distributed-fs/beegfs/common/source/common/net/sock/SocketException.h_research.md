<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketException.h

### Purpose
`SocketException.h` declares the base named exception for BeeGFS socket-layer errors.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDEXCEPTION(SocketException, "SocketException")`.

### Control Flow
Socket implementations throw this for generic socket, epoll, bind, listen, shutdown, and option errors.

### State, Persistence, And Dependencies
Exception message state is handled by the macro-defined type. It depends on `NamedException`.

### Integration Points
All socket exception subclasses derive from this base, allowing broad socket error handling.

### Risks
Tests should ensure broad catches do not hide cases where callers need the more specific timeout/connect/disconnect subclasses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketException.h -->
