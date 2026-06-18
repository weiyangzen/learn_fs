# Research: sources/distributed-fs/openafs/src/rx/rx_lwp.c

## sources/distributed-fs/openafs/src/rx/rx_lwp.c

### Purpose
`rx_lwp.c` implements RX's user-space LWP threading backend, including sleeps/wakeups, listener and server process startup, select/event integration, packet receive dispatch, socket registration, and sendmsg/recvmsg wrappers.

### Important Functions and State
- Thread primitives: `rxi_Sleep`, `rxi_Wakeup`, `rxi_Delay`, `rxi_InitializeThreadSupport`.
- Listener control: `rxi_StopListener`, `rxi_ReScheduleEvents`, `rxi_StartListener`, static `rx_ListenerProc`, and internal `rxi_ListenerProc`.
- Server startup: `rxi_StartServerProc`, `rx_ServerProc`.
- Socket integration: `rxi_Listen`, `rxi_Recvmsg`, `rxi_Sendmsg`.
- Globals: `debugSelectFailure`, `rx_listenerPid`, and static `quitListening`.

### Control Flow
Initialization sets up LWP and IOMGR support and clears `rx_selectMask`. `rxi_StartListener` creates a high-priority listener LWP. The listener loop allocates or reuses a receive packet, raises due RX events to compute the next select timeout, polls opportunistically when the last poll found data or every few seconds, otherwise calls `IOMGR_Select`, and dispatches readable sockets through `rxi_ReadPacket` and `rxi_ReceivePacket`. If a new server call is found, the listener trades into `rxi_ServerProc`; server workers similarly alternate between serving and listening, implementing the hot-thread style handoff.

`rxi_Sendmsg` simulates blocking send on a nonblocking socket by retrying `sendmsg`, waiting with `select` on writable readiness for `EWOULDBLOCK`/`ENOBUFS` and Linux-specific tolerated errors.

### State and Persistence
All state is in-memory. The select mask and min/max socket descriptors are global RX state. No durable persistence.

### Dependencies and Integration Points
Depends on LWP/IOMGR, `rx_globals.h`, `rx_internal.h`, `rx_stats.h`, packet allocation/read functions, event scheduler, and optional registration/swap-name callbacks. Integrates with non-pthread RX user-space service loops.

### Risks and Edge Cases
- `FD_SETSIZE` and descriptor bounds matter; `rxi_Listen` rejects descriptors beyond the configured size.
- Listener/server role swapping is subtle and relies on returned `newcall`/thread IDs.
- Select errors increment a debug counter but otherwise continue.
- `rxi_Sendmsg` returns negative errno-style values on some paths and `-1` on others.
- Nonblocking sockets and tolerated Linux UDP errors require careful behavior under packet loss or ICMP errors.

### Test Signals
Integration tests should cover LWP server startup, listener wakeup from new earlier events, socket registration bounds, packet receive dispatch, listener stop, send retry behavior under `EWOULDBLOCK`/`ENOBUFS`, and hot-thread handoff.
