<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.h -->
## sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.h

### Purpose
This header declares `RDMASocketImpl`, the concrete RDMA socket implementation hidden behind the common `RDMASocket` interface.

### Important APIs, Types, And Functions
The class overrides the full stream-style socket surface: connect, bind, listen, accept, shutdown, send/receive, timeout receive, connection checks, and delayed event checks. It stores an `IBVSocket*`, the pollable fd, and `IBVCommConfig`. Inline setters configure buffer count/size, RDMA timeouts, type of service, and test-only connection rejection rate.

### Control Flow
Consumers instantiate through factory callbacks rather than constructing this class directly. Accepted sockets use a private constructor that adopts a prepared `IBVSocket` and peer identity.

### State, Persistence, And Dependencies
The header depends on `IPAddress`, `IBVSocket`, and `RDMASocket`. Runtime state is volatile socket and RDMA queue state, not persisted across process restarts.

### Integration Points
This declaration is part of the `beegfs_ib` shared library and supplies the ABI used by the common RDMA socket factory. The exported `beegfs_socket_impl` symbol is declared here for plugin lookup.

### Risks
The class owns a raw `IBVSocket*` and relies on destructor cleanup. Inline configuration methods can be called after connection, but comments warn some options no longer take effect.

### Test Signals
Compile/link tests should verify overrides match `RDMASocket`. Runtime tests should validate fd selection before and after listen/connect/accept and ensure destruction releases adopted `IBVSocket` instances exactly once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/ib_lib/RDMASocketImpl.h -->
