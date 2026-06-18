
# sources/distributed-fs/ceph-client/include/uapi/linux/inet_diag.h

## Purpose

`inet_diag.h` defines the inet socket diagnostics netlink ABI used to query TCP, DCCP, raw, and related sockets, including request/response layouts, bytecode filters, extension IDs, memory/congestion-control info, and socket option snapshots. The complete 248-line file was read.

## Important APIs, Types, and Functions

Important types include `inet_diag_sockid`, `inet_diag_req`, `inet_diag_req_v2`, `inet_diag_req_raw`, `inet_diag_bc_op`, `inet_diag_hostcond`, `inet_diag_markcond`, `inet_diag_msg`, `inet_diag_meminfo`, `inet_diag_sockopt`, `tcpvegas_info`, `tcp_dctcp_info`, `tcp_bbr_info`, and `tcp_cc_info`. Enums define request attributes, bytecode operations, timers, diagnostic extensions, ULP info attributes, and constants such as `INET_DIAG_NOCOOKIE`.

## Control Flow

User space sends netlink diagnostic requests with address family, protocol, state mask, socket identity, and optional bytecode filters. Kernel diag handlers scan socket tables, apply filters, and return `inet_diag_msg` plus requested extensions.

## State and Persistence Behavior

The header defines snapshots of live socket state. Socket queues, timers, uid/inode, congestion-control metrics, marks, cgroup IDs, and ULP info are owned by protocol stacks and reported at dump time.

## Dependencies and Integration Points

It includes `linux/types.h` and integrates with `NETLINK_SOCK_DIAG`, TCP/DCCP/raw protocol tables, BPF storage reporting, TLS/MPTCP ULPs, cgroups, and tools such as `ss`.

## Risks and Edge Cases

`idiag_ext` in v2 is only 8 bits, so later extensions have special request aliases. Flexible address arrays and bytecode jumps require bounds checks. Cookie matching, CAP_NET_ADMIN-gated mark data, and raw protocol aliasing through `pad` are compatibility-sensitive.

## Test Signals

Socket diag tests should cover IPv4/IPv6 TCP/DCCP/raw requests, state masks, bytecode filters, extension dumps, congestion-control structs, ULP info, mark/cgroup/BPF storage attributes, and malformed filter rejection.
