<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.h -->
## sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.h

### Purpose
`RDMASocket.h` defines the abstract RDMA socket interface and the dynamic implementation callback table.

### Important APIs, Types, And Functions
`RDMASocket` derives from `PooledSocket`. `ImplCallbacks` contains function pointers for device existence, fork initialization, and socket creation. Static methods report availability and create instances. Pure virtual RDMA-specific APIs include connection checks, nonblocking receive checks, delayed event checks, buffer/timeouts/type-of-service configuration, and connection rejection-rate configuration.

### Control Flow
Concrete implementations are supplied by the dynamically loaded RDMA library. Callers should check availability before `create()` unless they are prepared for exceptions.

### State, Persistence, And Dependencies
The header holds no state; concrete RDMA implementations hold connection state. It depends on `PooledSocket`.

### Integration Points
Connection pools use this interface polymorphically with `StandardSocket`. Debug code can adjust rejection rates through the virtual API.

### Risks
The interface is an ABI boundary with `libbeegfs_ib.so`; changes require coordinated library updates. Tests should validate every callback path and polymorphic behavior expected by `NodeConnPool`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs/common/source/common/net/sock/RDMASocket.h -->
