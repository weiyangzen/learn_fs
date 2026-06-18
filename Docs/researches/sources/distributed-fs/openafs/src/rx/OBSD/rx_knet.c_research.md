# sources/distributed-fs/openafs/src/rx/OBSD/rx_knet.c

Purpose: OpenBSD Rx kernel listener socket send/receive support.

Important APIs/types/functions: `osi_NetReceive`, `osi_StopListener`, and `osi_NetSend`.

Control flow: receive builds a kernel `uio`, drops AFS global lock, calls `soreceive` with version-specific extra argument on OpenBSD 4.5+, restores the lock, copies peer address from returned mbuf, and handles stop-event sleep. Stop closes `rx_socket` and signals listener pid. Send builds an `MT_SONAME` mbuf, sends with `sosend`, and frees the address mbuf.

State/persistence: `rx_socket`, `rxk_ListenerPid`, socket mbufs, and OpenAFS termination state.

Dependencies/integration: OpenBSD socket/uio/mbuf APIs and OpenAFS listener lifecycle.

Risks: pseudo-locking in matching mutex header limits concurrency safety; close-before-signal ordering can race with receiver cleanup; API signature varies by OpenBSD version. Test signals are OpenBSD listener send/receive, shutdown, and version-specific compile coverage.
