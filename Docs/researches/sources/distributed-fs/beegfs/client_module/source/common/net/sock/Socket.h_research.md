# sources/distributed-fs/beegfs/client_module/source/common/net/sock/Socket.h

Purpose: Declares the abstract BeeGFS kernel socket API and common send/receive helpers.

Important APIs/types/functions: `SocketOps` defines virtual `connectByIP`, `bindToAddr`, `listen`, `shutdown`, `shutdownAndRecvDisconnect`, `sendto`, and `recvT`. Inline helpers include `Socket_virtualDestruct`, `Socket_recvT`, kernel-buffer wrappers, exact-receive loops, and send wrappers.

Control flow: Public helpers copy or construct `iov_iter` values, delegate to the concrete vtable, and advance iterators after successful reads. Exact receive loops continue until the requested byte count arrives or a timeout/error occurs.

State and persistence behavior: The base stores peer names/IP, bound port, and poll state. No durable persistence; activity is owned by concrete sockets.

Dependencies and integration points: Shared by standard TCP sockets, RDMA sockets, ack helper, message transport, and kernel `iov_iter` utilities.

Risks: The header notes iterator advancement issues, especially for `ITER_PIPE`; callers must avoid double-advancing or mutating external pipe state unexpectedly. Exact receive requires initialized `outNumReceivedBeforeError`.

Test signals: Partial reads, timeout/error handling, iterator advancement, kernel-buffer wrappers, and vtable dispatch.
