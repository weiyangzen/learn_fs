# sources/distributed-fs/ceph-client/include/uapi/linux/tcp.h

## Purpose
Defines the TCP protocol UAPI: wire header layout, flag words, socket options, repair/diagnostic/authentication structs, `TCP_INFO`, timestamping stats attributes, MD5/TCP-AO key management, and zero-copy receive control.

## Important APIs, Types, and Constants
`struct tcphdr` maps the TCP wire header with endian-dependent bitfields; `union tcp_word_hdr`, `tcp_flag_word()`, and `TCP_FLAG_*` provide flag access. Socket options include classic controls (`TCP_NODELAY`, `TCP_MAXSEG`, keepalive, congestion, MD5), repair (`TCP_REPAIR*`), Fast Open, ULP, zero-copy receive, `TCP_INQ`, TCP-AO, MPTCP query, and RTO/delayed-ACK bounds. `struct tcp_info` exports extensive connection state, congestion, RTT, pacing, ECN, retransmission, and byte counters. Authentication structs include `tcp_md5sig`, `tcp_diag_md5sig`, `tcp_ao_add`, `tcp_ao_del`, `tcp_ao_info_opt`, `tcp_ao_getsockopt`, and `tcp_ao_repair`. `struct tcp_zerocopy_receive` drives zero-copy receive mapping.

## Control Flow, State, and Persistence
Applications use `setsockopt()`/`getsockopt()` to configure or query per-socket TCP state. Kernel TCP state machines own runtime state; options mutate congestion, repair, authentication keys, Fast Open, queues, and zero-copy behavior. Structs are append-only ABI where old userspace may request shorter sizes.

## Dependencies and Integration Points
Depends on `<linux/types.h>`, `<asm/byteorder.h>`, and `<linux/socket.h>`. Integrates with TCP stack, inet_diag, timestamping cmsgs, MPTCP, crypto/authentication, and high-performance networking applications.

## Risks and Test Signals
Risks include endian bitfield mistakes, `tcp_info` extension compatibility, authentication reserved fields not zeroed, key leakage, and zero-copy pointer/length validation. Test header flag parsing on both endian models, `TCP_INFO` length negotiation, MD5/AO key add/delete/list, repair mode, Fast Open failure reporting, zero-copy receive error paths, and 32-bit compat.
