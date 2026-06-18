# sources/distributed-fs/ceph-client/net/ipv4/tcp_diag.c

## Purpose
`tcp_diag.c` registers the TCP handler for SOCK_DIAG/INET_DIAG netlink monitoring. It dumps TCP socket state, one-socket lookups, optional destruction requests, TCP info, memory and queue data, MD5 signature metadata for privileged callers, and ULP-specific diagnostic data.

## Important APIs, Types, And Functions
The central registration object is `static const struct inet_diag_handler tcp_diag_handler`. Important functions are `tcp_diag_get_info()`, `tcp_diag_get_aux()`, `tcp_diag_get_aux_size()`, `tcp_twsk_diag_fill()`, `tcp_req_diag_fill()`, `sk_diag_fill()`, `tcp_diag_dump()`, `tcp_diag_find_one_icsk()`, `tcp_diag_dump_one()`, and optional `tcp_diag_destroy()`. MD5 helpers are conditional on `CONFIG_TCP_MD5SIG`; destroy support is conditional on `CONFIG_INET_DIAG_DESTROY`.

## Control Flow
Netlink dump requests enter `tcp_diag_dump()`. It walks listen hash buckets, bound-inactive sockets, and established hash buckets according to requested state masks and family/port/bytecode filters. To avoid holding bucket locks while filling skb messages, established and bound walks batch up to `SKARR_SZ` sockets with references, release locks, then call `inet_sk_diag_fill()` or `sk_diag_fill()`. Time-wait and request sockets have specialized fill functions because their layouts differ from full sockets. Single-socket requests use `tcp_diag_find_one_icsk()` to look up IPv4, IPv6, or v4-mapped flows, check cookies, allocate a reply skb sized by `tcp_diag_get_aux_size()`, and unicast the result.

## State, Persistence, Dependencies, And Integration
The file does not own persistent TCP state; it snapshots socket and request state under appropriate locks and references. It depends on inet hash tables, inet_diag common fill helpers, netlink capability checks, ULP callbacks, MD5 key storage, timewait layout compatibility, and per-net `diag_nlsk`. It integrates with user tools such as `ss` through NETLINK_SOCK_DIAG.

## Risks And Test Signals
Risks include bucket-walk cursor bugs, reference leaks, netns filtering mistakes, message-size underestimation causing `-EMSGSIZE`, leaking MD5 data without `CAP_NET_ADMIN`, and structure-layout assumptions for timewait/request sockets. Tests should dump listeners, established, timewait, SYN_RECV, and bound-inactive sockets; exercise IPv4, IPv6, and v4-mapped lookup; request ULP and MD5 attributes with and without privilege; validate continuation cursors under small receive buffers; and test optional destroy behavior.
