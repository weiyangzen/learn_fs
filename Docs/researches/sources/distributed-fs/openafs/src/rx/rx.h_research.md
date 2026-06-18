# Research: sources/distributed-fs/openafs/src/rx/rx.h

## sources/distributed-fs/openafs/src/rx/rx.h

### Purpose
`rx.h` is the main public and semi-public RX protocol header. It exposes connection, call, peer, service, security-class, statistics, debug, packet, acknowledgement, and RPC-operation-stat interfaces used by both user-space and kernel RX builds.

### Important APIs, Types, and Constants
- Declares accessors implemented by `rx_conn.c`, `rx_call.c`, and peer code: `rx_GetConnectionEpoch`, `rx_GetConnectionId`, `rx_SetSecurityData`, `rx_SecurityObjectOf`, `rx_ConnectionOf`, `rx_Error`, `rx_GetCallStatus`, `rx_HostOf`, and related helpers.
- Defines packet classes (`RX_PACKET_CLASS_RECEIVE`, `SEND`, `SPECIAL`, continuation buffers), packet type strings, `RX_MAXIOVECS`, and call state/mode/flag constants used by `rx.c`, `rx_rdwr.c`, debug tools, and rxdebug protocol structures.
- Defines default timing and sizing constants: `RX_IDLE_DEAD_TIME`, `RX_DEFAULT_DEAD_TIME`, `RX_MAX_SERVICES`, `RX_MAXCALLS`, `RX_CIDSHIFT`, `RX_CHANNELMASK`, `RX_MAXACKS`, challenge/check-reach timers, and RX error values.
- Defines `struct rx_service`, the installed server service descriptor containing service identity, socket, security classes, execution hooks, per-service concurrency bounds, dead/idle timing, and service-specific data.
- Defines `struct rx_ackPacket`, including buffer-space, skew, first packet, previous packet, serial, reason, and up to 255 ACK/NACK bytes.
- Defines the security API surface: `rx_securityIndex`, security type constants, `struct rx_securityObjectStats`, `rx_securityConfigVariables`, `struct rx_securityClass`, and `RXS_*` dispatch macros.
- Defines wire/debug/stat structures: `struct rx_statistics`, `struct rx_debugIn`, `struct rx_debugStats`, `struct rx_debugConn_vL`, `struct rx_debugConn`, `struct rx_debugPeer`, `rx_function_entry_v1_t`, and `rx_interface_stat_t`.
- Provides macros for common user APIs: `rx_Read`, `rx_Write`, `rx_Readv`, `rx_Writev`, `rx_MaxUserDataSize`, service setters, tranquil mode, abort throttling, and hot-thread controls.

### Control Flow and Integration
This header is not executable control flow, but it defines the contracts consumed throughout RX. `rx.c` owns most lifecycle, packet processing, and call state transitions; `rx_conn.c` and `rx_call.c` provide accessor implementations for the opaque structures; `rx_rdwr.c` consumes the read/write macros; security classes use `RXS_*` hooks during connection setup, packet preparation, challenge/response, packet checking, and destruction. Debug and statistics structures are serialized by rxdebug and RPC stats retrieval code, so field order and version constants are part of the compatibility contract.

### State and Persistence Behavior
All state described here is in-memory process or kernel state. `struct rx_service` persists for the RX process lifetime after service registration. Ack, debug, and statistics structures are transient or exported snapshots. No durable storage is managed here, but the debug/stat structures are wire-visible and therefore persistent compatibility formats.

### Dependencies and Integration Points
The header selects platform headers and thread backends (`rx_kmutex.h`, `rx_kernel.h`, `rx_pthread.h`, `rx_lwp.h`, `rx_user.h`) based on `KERNEL`, `AFS_PTHREAD_ENV`, and `AFS_NT40_ENV`. It depends on `rx_clock.h`, `rx_event.h`, `rx_misc.h`, `rx_null.h`, `rx_multi.h`, and `rx_prototypes.h`. It is an integration hub for RX security modules such as rxnull, rxkad, rxgk, and Kerberos-related classes.

### Risks and Edge Cases
- Debug/stat structures are externally consumed; changing fields, sizes, or version constants can break rxdebug and stats clients.
- `rx_MaxUserDataSize` assumes call MTU and security overhead fields are initialized and consistent.
- Ack packet sizing uses `offsetof` and variable `acks` count; off-by-one changes can corrupt wire parsing.
- Macros write directly to globals and service fields without validation in many cases.
- `rx_securityClass.refCount_data` is deliberately opaque; direct access risks ABI and synchronization bugs.

### Test Signals
Useful tests include rxdebug compatibility checks across versions, unit or integration tests for ACK encoding/decoding and max user data calculations, service registration/startup tests under each threading backend, security class hook tests, and RPC stats retrieval/marshalling tests that verify old clients tolerate current structures.
