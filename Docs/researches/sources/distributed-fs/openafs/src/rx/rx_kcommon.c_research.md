# Research: sources/distributed-fs/openafs/src/rx/rx_kcommon.c

## sources/distributed-fs/openafs/src/rx/rx_kcommon.c

### Purpose
`rx_kcommon.c` contains shared in-kernel RX support across platforms: kernel UDP socket creation/closing, RX port registration, listener startup, packet allocation/arrival adapters, peer MTU/interface initialization, interface enumeration, event daemon support, listener loops, packet receive, messaging, and panic/assertion helpers.

### Important Functions and State
- Port/socket tracking: `rxk_ports`, `rxk_portRocks`, `rxk_AddPort`, `rxk_DelPort`, `rxk_shutdownPorts`, `rxi_GetHostUDPSocket`, and `rxi_GetUDPSocket`.
- Utility/assertion: `osi_utoa`, `osi_AssertFailK`, `osi_Msg`, and `osi_Panic`.
- Kernel server/listener: `rx_ServerProc`, `MyPacketProc`, `MyArrivalProc`, `rxi_StartListener`, `afs_rxevent_daemon`, `rxk_ReadPacket`, `rxk_Listener`, and platform-specific `osi_StopListener`.
- Peer/interface sizing: `rxi_InitPeerParams`, `rxi_GetcbiInfo`, `rxi_Findcbi`, `rxi_GetIFInfo`, and `rxi_FindIfnet`.
- Socket lifecycle: `rxk_NewSocketHost`, `rxk_NewSocket`, and `rxk_FreeSocket` for supported non-Linux/non-Sun/non-sockproxy platforms in this common path.
- Globals: `rxk_PacketArrivalProc`, `rxk_GetPacketProc`, `rxk_initDone`, static local interface address/MTU arrays, and listener PID/task globals in listener builds.

### Control Flow
RX kernel initialization calls `rxi_GetHostUDPSocket` to create/bind a UDP socket via `rxk_NewSocketHost`, then registers the bound port. `rxi_StartListener` either installs packet allocation/arrival callbacks and calls `rxk_init`, or platform listener builds run `rxk_Listener`. Incoming packets are allocated by `MyPacketProc` or `rxk_ReadPacket`, decoded, and passed to `rxi_ReceivePacket`; returned packet buffers are freed. Server worker threads reserve packets and quotas before entering `rxi_ServerProc`.

Peer initialization calls interface discovery on demand, finds the best interface for a remote address, sets retransmission timeout defaults, derives interface MTU after IP/UDP/RX overhead, clamps to RX send/receive limits, initializes NAT/max MTU and datagram packet counts, and starts congestion control at one packet. The event daemon periodically calls `rxevent_RaiseEvents` and transitions `afs_termState` through shutdown states.

### State and Persistence
State is kernel memory only: registered RX ports, socket pointers, interface caches, listener PID/task, packet callbacks, and global RX tuning. No durable persistence.

### Dependencies and Integration Points
Depends on extensive kernel networking headers via `rx_kcommon.h`, `rx_packet.h`, `rx_internal.h`, `rx_stats.h`, `rx_peer.h`, `afs/opr.h`, `afsint.h`, and platform socket APIs (`socreate`, `sobind`, `soreserve`, `soclose`, `sock_socket`, `osi_NetReceive`). It integrates with `rx.c` packet processing, `rx_event.c`, AFS global lock macros, and platform shutdown state.

### Risks and Edge Cases
- Platform preprocessor paths are numerous; compile coverage is the main risk.
- Port registration has a fixed `MAXRXPORTS` limit and no locking in the common code shown.
- `rxk_shutdownPorts` conditionally closes sockets; incorrect build macros can leak or double-close.
- Packet receive sizes are inferred partly from maximum advertised receive size because the RX header lacks a full packet length.
- Interface cache update logic includes complex platform loops and must handle vnet/epoch locking correctly.
- Kernel socket setup uses platform-specific allocation and cleanup; error paths can be hard to validate.

### Test Signals
Kernel build matrix coverage is essential. Runtime signals include successful bind/listen/shutdown, packet receive/decode under jumbo and small packet sizes, interface MTU derivation, peer timeout selection, listener wakeup on shutdown, event daemon shutdown state transitions, and panic/assert formatting tests where possible.
