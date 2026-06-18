# sources/distributed-fs/openafs/src/rx/UKERNEL/rx_knet.c

Purpose: user-space Rx kernel network emulation using POSIX sockets and Rx listener/server loops.

Important APIs/types/functions: `struct usr_socket`, globals `usr_rx_port`, `usr_ifnet`, `usr_in_ifaddr`; `afs_rxevent_daemon`, `rxi_ListenerProc`, `rxk_Listener`, `rx_ServerProc`, `rxk_NewSocketHost`, `rxk_NewSocket`, `rxk_InitializeSocket`, `rxk_FreeSocket`, `osi_StopListener`, `osi_NetSend`, `shutdown_rxkernel`, `rx_Finalize`, and `rxi_Recvmsg`.

Control flow: socket allocation is deferred: `rxk_NewSocketHost` allocates a wrapper, and `rxk_InitializeSocket` later creates/binds a UDP socket, sets buffers, and updates `rx_port`. Listener loops allocate packets, read with `rxi_ReadPacket`, deliver via `rxi_ReceivePacket`, and may become server threads; server threads can become listeners. Event daemon periodically raises Rx events and timed waits until termination.

State/persistence: `struct usr_socket` with fd and bound port, `usr_rx_port`, Rx termination state, receive/send socket buffers, `rx_port`, and Rx thread counts.

Dependencies/integration: POSIX socket APIs, user threading/sleep, Rx packet/server internals, OPR/global locks, and UKERNEL AFS shutdown.

Risks: `rxk_FreeSocket` is a stub and does not close fd; `rx_Finalize` asserts; send asserts full datagram length; listener/server role switching is subtle. Test signals are UKERNEL loopback RPCs, event daemon shutdown, socket buffer setup, sendmsg error handling, and fd leak checks.
