# sources/distributed-fs/openafs/src/rx/SOLARIS/rx_knet.c

Purpose: Solaris Rx kernel socket and network-interface integration.

Important APIs/types/functions: dynamically resolved `sockfs_*` function pointers; `rxi_GetIFInfo`, `rxi_FindIfMTU`, `rxk_NewSocketHost`, `rxk_NewSocket`, `osi_FreeSocket`, `osi_NetSend`, `osi_NetReceive`, `osi_StartNetIfPoller`, `osi_NetIfPoller`, `osi_StopNetIfPoller`, `shutdown_rxkernel`, and `osi_StopListener`.

Control flow: socket creation resolves sockfs symbols with `modlookup`, creates/binds a UDP sonode, and sets send/receive buffers. Send/receive wrap `sockfs_sosendmsg`/`sockfs_sorecvmsg` with kernel `nmsghdr` and `uio`. Interface discovery either walks IP structures or, on Solaris 10+, polls `/dev/udp` via LDI ioctls into `afsifinfo`, then derives Rx MTUs and receive limits.

State/persistence: cached local addresses/MTUs, sockfs function pointers, global `rx_sockaddr`, `afsifinfo`, interface poll timeout id, taskq and lock state, `rx_socket`, and listener pid.

Dependencies/integration: Solaris sockfs, STREAMS/IP internals, LDI, task queues, Rx MTU helpers, OpenAFS shutdown state.

Risks: unresolved sockfs symbols fail socket creation; error paths leak created sonodes in some early-return cases; interface polling stores `lifr_addrlen` as netmask and may be platform-sensitive; EINTR cleanup mutates current signal state. Test signals are Solaris 9/10+ builds, socket bind/send/receive, interface polling updates, shutdown of poller/listener, and MTU selection.
