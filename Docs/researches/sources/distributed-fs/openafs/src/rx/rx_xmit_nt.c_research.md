# sources/distributed-fs/openafs/src/rx/rx_xmit_nt.c

## Purpose
Provides Windows implementations of `sendmsg` and `recvmsg` semantics for RX, using Winsock extension functions when available and copy-based fallbacks otherwise.

## Important APIs, Types, And Functions
The file defines extension function pointers `pWSARecvMsg` and `pWSASendMsg`, initializes them in `rxi_xmit_init`, and implements `recvmsg(osi_socket socket, struct msghdr *msgP, int flags)` and `sendmsg(osi_socket socket, struct msghdr *msgP, int flags)` under `AFS_NT40_ENV`.

## Control Flow
`rxi_xmit_init` fetches `WSARecvMsg` and `WSASendMsg` via `WSAIoctl`, enables UDP connection-reset notifications and circular queueing. `recvmsg` uses `WSARecvMsg` if present; otherwise it receives into a temporary packet-sized buffer with `recvfrom` and copies into caller iovecs. `sendmsg` uses `WSASendMsg` if present; otherwise it sends directly from the first iovec when there are at most two iovecs, or packs multiple iovecs into a temporary buffer before `sendto`. Winsock errors are mapped to `errno` values expected by RX.

## State And Persistence
State is limited to cached Winsock extension function pointers. No disk persistence exists.

## Dependencies And Integration Points
It depends on Windows Winsock headers, `rx.h`, `rx_globals.h`, `rx_packet.h`, and `rx_xmit_nt.h`. `rx_packet.c` and `rx_pthread.c` call `rxi_Recvmsg`/`rxi_Sendmsg`, which ultimately use these macros/functions on NT builds.

## Risks And Test Signals
Risks include strong assumptions that the first two RX iovecs are physically contiguous, fallback stack buffers capped at `RX_MAX_PACKET_SIZE`, partial-copy behavior on receive truncation, and global extension pointers initialized per socket but shared process-wide. Test signals include Windows RX client/server traffic, jumbo and multi-iovec sends, WSA extension unavailable fallback, WSAEWOULDBLOCK/ECONNRESET handling, and host-unreachable propagation.
