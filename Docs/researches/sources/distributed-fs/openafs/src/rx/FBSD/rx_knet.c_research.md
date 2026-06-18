# sources/distributed-fs/openafs/src/rx/FBSD/rx_knet.c

Purpose: FreeBSD Rx kernel network send/receive and legacy UDP interception support.

Important APIs/types/functions: listener-mode `osi_NetReceive`, `osi_StopListener`, `osi_NetSend`; non-listener `rxk_init`, `rxk_input`, `rxk_fasttimo`, `trysblock`, and alternate mbuf-building `osi_NetSend`.

Control flow: in listener mode, receive and send wrap `soreceive`/`sosend` with copied iovec arrays and dropped AFS global lock; stop shuts down the socket, signals the listener, pokes it with a loopback byte, waits for `rxk_ListenerPid` to clear, then closes. The old non-listener path hooks UDP protosw input/timer, checks Rx ports, validates UDP length/checksum, converts mbufs to Rx packets, and falls through to UDP otherwise.

State/persistence: listener pid, `rx_socket`, `parent_proto`, `rxk_initDone`, `rxk_ports`, `rxk_portRocks`, and socket buffer lock bits in legacy path.

Dependencies/integration: FreeBSD sockets, mbufs, protosw, Rx packet hooks, Rx event timer, and OpenAFS sleep/wakeup.

Risks: non-listener code is marked almost working; manual socket-buffer locking at interrupt level is fragile; stop path relies on listener pid lifecycle; copied iovec bounds must respect `RX_MAXIOVECS`. Test signals are listener receive/send, stop/restart, signal wakeup, oversized iovec panic, and legacy builds if enabled.
