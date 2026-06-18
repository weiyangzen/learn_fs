# sources/distributed-fs/openafs/src/rx/DARWIN/rx_knet.c

Purpose: Darwin/macOS Rx kernel network support across direct kernel sockets, listener mode, upcall mode, and modern userspace socket proxy mode.

Important APIs/types/functions: `osi_NetSend`, `osi_NetReceive`, `osi_StopListener`, `osi_StopNetIfPoller`, `rxk_NewSocketHost`, `rxk_NewSocket`, `rx_upcall`, `rx_upcall_common`, `SockProxyRequest`, `rxk_SockProxyReply`, `rxk_SockProxySetup`, and `rxk_SockProxyFinish`.

Control flow: direct paths send/receive through `sock_send`, `sock_receivembuf`, `sosend`, or `soreceive` while dropping the AFS global lock. Upcall mode allocates an Rx packet, receives/copies payload into Rx wire vectors, decodes and validates headers, updates stats, and hands packets to `rxi_ReceivePacket`. Sockproxy mode delegates socket start/send to afsd userspace processes through a mutex/CV request queue and receives packets via syscall replies.

State/persistence: sockproxy keeps per-process request slots, a queue of idle workers, shutdown state, a fake `SockProxySocket`, and `afs_sockproxy_procs`. Packet stats update `rx_stats`.

Dependencies/integration: Darwin socket/mbuf APIs, Rx packet internals, OpenAFS termination states, afsd sockproxy syscall protocol, OPR queues, and global locking.

Risks: sockproxy request/reply ownership is delicate; shutdown must wake or kill receiver processes; packet length and extra-buffer handling guard against overreads; direct paths vary by Darwin version. Tests should cover sockproxy startup/send/recv/shutdown, direct listener mode, malformed packets, signal/termination paths, and jumbo receive sizing.
