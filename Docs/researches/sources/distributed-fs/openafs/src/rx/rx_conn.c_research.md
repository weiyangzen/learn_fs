# Research: sources/distributed-fs/openafs/src/rx/rx_conn.c

## sources/distributed-fs/openafs/src/rx/rx_conn.c

### Purpose
`rx_conn.c` provides public accessor and mutator functions for `struct rx_connection`, isolating callers from internal connection layout.

### Important Functions
- Accessors: `rx_GetConnectionEpoch`, `rx_GetConnectionId`, `rx_GetSecurityData`, `rx_IsUsingPktCksum`, `rx_GetSecurityHeaderSize`, `rx_GetSecurityMaxTrailerSize`, `rx_IsServerConn`, `rx_IsClientConn`, `rx_PeerOf`, `rx_ServiceIdOf`, `rx_SecurityClassOf`, `rx_SecurityObjectOf`, `rx_ServiceOf`, and `rx_ConnError`.
- Mutators: `rx_SetSecurityData`, `rx_SetSecurityHeaderSize`, `rx_SetSecurityMaxTrailerSize`, and `rx_SetMsgsizeRetryErr`.

### Control Flow and State
All functions are direct field reads or writes. They do not allocate, lock, or persist state. Mutators update security-related overhead and retry behavior that are later consumed by packet sizing and send error handling.

### Dependencies and Integration Points
Includes `rx.h` and `rx_conn.h`. Used by security modules, connection cache, RPC callers, debug code, and packet sizing macros such as `rx_MaxUserDataSize`.

### Risks and Edge Cases
- No synchronization is performed; callers must respect connection lock ownership.
- Security header/trailer sizes directly affect max payload calculations and can cause packet sizing errors if changed after active calls begin.
- `rx_ConnError` is a snapshot and may race with connection error transitions.

### Test Signals
Tests should cover security module setup of header/trailer sizes, msgsize retry error propagation, and accessor correctness for client/server connections.
