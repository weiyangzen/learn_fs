# sources/distributed-fs/openafs/src/rx/NBSD/rx_knet.c

Purpose: NetBSD Rx kernel listener socket send/receive support.

Important APIs/types/functions: `osi_NetReceive`, `osi_StopListener`, and `osi_NetSend`.

Control flow: receive copies iovecs into a local array, configures a kernel `uio`, drops AFS global lock, calls `soreceive`, restores the lock, updates the received length, and copies returned sockaddr data from an mbuf. Stop shuts down and closes `rx_socket`, signals the listener pid, and uses NetBSD socket locking helpers. Send builds a `uio` plus `MT_SONAME` mbuf for the destination and calls `sosend`.

State/persistence: `rx_socket`, `rxk_ListenerPid`, socket shutdown state, and returned mbuf address ownership.

Dependencies/integration: NetBSD socket, mbuf, proc, and uio APIs plus OpenAFS listener state.

Risks: receive waits during `AFSOP_STOP_RXEVENT` can stall shutdown; sockaddr mbuf length is trusted; version-specific `UIO_SETUP_SYSSPACE` and `osi_curproc` must match kernel APIs. Test signals are NetBSD listener loopback, stop path, excessive iovec panic, and restart after shutdown.
