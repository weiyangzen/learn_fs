<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketConnectException.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/SocketConnectException.h

### Purpose
`SocketConnectException.h` declares the named exception type for connection-establishment failures.

### Important APIs, Types, And Functions
It uses `DECLARE_NAMEDSUBEXCEPTION(SocketConnectException, "SocketConnectException", SocketException)`.

### Control Flow
Socket implementations throw this subclass for hostname resolution, connect timeout, and failed local socket-pair creation paths.

### State, Persistence, And Dependencies
There is no state beyond exception message data supplied by the macro base. It depends on `SocketException`.

### Integration Points
Connection pools catch this type to distinguish connect failures from established-connection disconnects.

### Risks
Tests should verify catch ordering, name string, and that connect failure paths throw this subclass rather than generic `SocketException`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/SocketConnectException.h -->
