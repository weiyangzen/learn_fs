
# sources/distributed-fs/ceph-client/include/uapi/linux/if_pppol2tp.h

## Purpose

`if_pppol2tp.h` defines socket address and socket-option UAPI structures for PPP over L2TP, including IPv4/IPv6 and L2TPv2/L2TPv3 variants. The complete 105-line file was read.

## Important APIs, Types, and Functions

Structures are `pppol2tp_addr`, `pppol2tpin6_addr`, `pppol2tpv3_addr`, and `pppol2tpv3in6_addr`. Enums define `PPPOL2TP_SO_DEBUG`, `PPPOL2TP_SO_RECVSEQ`, `PPPOL2TP_SO_SENDSEQ`, `PPPOL2TP_SO_LNSMODE`, `PPPOL2TP_SO_REORDERTO`, plus deprecated debug category aliases mapped to `L2TP_MSG_*`.

## Control Flow

User space creates a PPPoL2TP socket and calls `connect()` with the matching address structure. Kernel PPPoL2TP code binds the socket to an existing UDP/IP tunnel fd, local/remote tunnel IDs, session IDs, and peer address; socket options then control sequencing, LNS mode, and reordering.

## State and Persistence Behavior

The header defines connection-time state passed into the kernel. Tunnel/session bindings and socket options persist on the PPPoL2TP socket and related L2TP session objects until disconnect/close or option changes.

## Dependencies and Integration Points

It includes `linux/types.h`, `linux/in.h`, `linux/in6.h`, and `linux/l2tp.h`. It integrates with PPP, L2TP, IPv4/IPv6 sockets, and AF_PPPOX protocol-specific sockaddr wrappers.

## Risks and Edge Cases

The main compatibility risks are 16-bit versus 32-bit tunnel/session IDs, pid/fd ownership semantics, IPv4 versus IPv6 layout selection, reorder timeout interpretation, and deprecated debug options that may be accepted but unused.

## Test Signals

Tests should connect v2/v3 and IPv4/IPv6 sessions, validate bad fd/pid/session combinations, exercise sequence send/receive options, and confirm LNS/reorder settings are reflected in session behavior.
