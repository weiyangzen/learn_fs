# Research: sources/distributed-fs/openafs/src/rx/rx_conn.h

## sources/distributed-fs/openafs/src/rx/rx_conn.h

### Purpose
`rx_conn.h` defines the internal RX connection object: an authenticated communication path with up to `RX_MAXCALLS` simultaneous call channels plus security, timing, NAT, and per-connection state.

### Important Fields
- Hash/free-list link, `peer`, optional locks/cv, epoch, CID, error, call pointers, per-channel call numbers/window values, busy timestamps, serial number, MTU probe state, and event pointers.
- Server/client role fields: `service`, `serviceId`, `type`, `securityIndex`, `securityObject`, and `securityData`.
- Timeout and liveness fields: `secondsUntilPing`, `timeout`, `lastSendTime`, `secondsUntilDead`, `hardDeadTime`, `idleDeadTime`, `secondsUntilNatPing`, and `natKeepAliveEvent`.
- Security overhead fields and `msgsizeRetryErr`.
- Connection-specific data array.

### Control Flow and State
The structure is allocated and initialized primarily by `rx.c`; it is searched and refcounted through connection hash tables and destroyed through RX lifecycle paths. It stores per-channel state needed to create and receive calls, and event pointers are used by challenge, delayed abort, reachability, and NAT keepalive scheduling.

### Dependencies and Integration Points
Used by `rx.c`, `rx_conn.c`, `rx_conncache.c`, security classes, debug/stat code, and call allocation. It relies on constants and flags defined in `rx.h` and peer state from `rx_peer`.

### Risks and Edge Cases
- Bottom bits of `cid` encode channel information; code must mask/shift consistently.
- Event pointer lifetime must be coordinated with connection refcounts.
- Cached connections set `RX_CONN_CACHED` and follow special release rules in `rx_conncache.c`.
- Security object and data lifetime is shared with security modules.

### Test Signals
Exercise multi-channel call allocation, connection timeout changes, NAT ping scheduling, security object attach/destroy, connection cache interactions, and debug export of connection fields.
