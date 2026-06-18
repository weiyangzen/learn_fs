# sources/distributed-fs/ceph-client/net/packet/diag.c

## Purpose
`diag.c` implements SOCK_DIAG monitoring for AF_PACKET sockets. It lets userspace dump packet socket state over `NETLINK_SOCK_DIAG`, including socket identity, packet-specific flags, multicast memberships, ring configuration, fanout configuration, memory info, and optionally attached filter info.

## Important APIs, types, and functions
The module registers `packet_diag_handler` for `AF_PACKET`. `packet_diag_handler_dump()` validates `struct packet_diag_req`, rejects unsupported protocol filtering, and starts a dump through `netlink_dump_start()`. `packet_diag_dump()` walks `net->packet.sklist` under `sklist_lock` and calls `sk_diag_fill()` for each socket.

`sk_diag_fill()` writes the base `packet_diag_msg`, socket cookie, inode, packet protocol, and requested attributes. Helper functions populate specific attributes: `pdiag_put_info()` maps `packet_sock` fields and flags into `packet_diag_info`; `pdiag_put_mclist()` serializes `packet_mclist` entries under RTNL; `pdiag_put_ring()` and `pdiag_put_rings_cfg()` report RX/TX ring geometry and V3 block settings under `pg_vec_lock`; `pdiag_put_fanout()` reports fanout id/type under `fanout_mutex`.

## Control flow and state
The module is query-only. A dump request enters `packet_diag_handler_dump()`, then `packet_diag_dump()` iterates the per-net packet socket list using `cb->args[0]` as a cursor. Each socket is encoded into a netlink message, and if the skb fills, the cursor is updated so a later dump callback resumes at the next socket.

No persistent state is created beyond registering the handler at module load. Diagnostic output is a snapshot of live socket state, with locking chosen to match the owning subsystem: packet socket list mutex for enumeration, RTNL for multicast list reads, `pg_vec_lock` for ring reads, and `fanout_mutex` for fanout reads.

## Dependencies and integration points
This file depends directly on `internal.h` for `packet_sock`, ring, fanout, and flag helpers. It integrates with the generic sock_diag framework, netlink dump control, packet socket per-net state initialized by `af_packet.c`, and capability checks in `sock_diag_put_filterinfo()` for filter visibility.

## Risks and edge cases
The main risks are snapshot consistency and privilege leakage. Ring/fanout/membership state can change during dumps, so helpers use local locks but do not provide a single global atomic snapshot. Filter dumping is gated by `may_report_filterinfo`, derived from `CAP_NET_ADMIN`; regressions could expose BPF details to unprivileged callers. Netlink sizing paths must cancel partial messages on `-EMSGSIZE` to avoid malformed dumps.

## Test signals
Tests should open AF_PACKET sockets with combinations of memberships, rings, fanout, filters, and aux/origdev/vnet flags, then query `ss`, `sock_diag`, or custom netlink clients. Expected signals are correct dump continuation across small receive buffers, correct permission-dependent filter attributes, correct V3 ring fields, and absence of races while sockets are closing or changing fanout/ring configuration.
