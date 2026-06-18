# sources/distributed-fs/beegfs/client_module/source/common/net/sock/StandardSocket.c

Purpose: Implements BeeGFS TCP/UDP kernel sockets on top of Linux `struct socket`, including callbacks, options, connect/bind/listen/shutdown, timed receive, and send/receive wrappers.

Important APIs/types/functions: `StandardSocket_init`, `_StandardSocket_initSock`, option setters for keepalive/broadcast/receive-buffer/TCP_NODELAY/TCP_CORK, `_StandardSocket_connectByIP`, `_bindToAddr`, `_listen`, `_shutdown`, `_shutdownAndRecvDisconnect`, `_recvT`, `_sendto`, `StandardSocket_recvfrom`, and `StandardSocket_recvfromT`.

Control flow: Initialization creates a kernel socket and installs callbacks that wake BeeGFS poll waiters. Connect and bind use `Beegfs_Sockaddr` helpers for IPv4/IPv6 compatibility. Timed receive uses socket wait state and returns timeout/error codes; send handles optional destination addresses.

State and persistence behavior: Owns a kernel socket pointer and restores/releases it on uninit. Poll wait queues and callback state live only while the socket exists.

Dependencies and integration points: Integrates Linux socket APIs, `IpAddress.h`, `SocketTk`, `Serialization`, `PooledSocket`, and BeeGFS transport code.

Risks: Kernel callback replacement/restoration, blocking waits, allocation mode, and IPv4/IPv6 fallback are sensitive to kernel-version behavior. Buffer-size tuning doubles requested values and may fail with kernel limits.

Test signals: Connect/bind/listen failure paths, callback wakeups, timeouts, UDP recvfrom, TCP options, IPv4-mapped and IPv6 addresses, and teardown under pending pollers.
