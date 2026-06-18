<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_diag.c -->
# sources/distributed-fs/ceph-client/net/mptcp/mptcp_diag.c

## Purpose
Registers an inet_diag handler for whole MPTCP sockets, supporting dump, single-socket lookup by token cookie, listener reporting, queue info, and `struct mptcp_info` export.

## Important APIs, Types, and Functions
`mptcp_diag_handler` is the registered `inet_diag_handler` for `IPPROTO_MPTCP`. `mptcp_diag_dump_one()` resolves sockets by token. `mptcp_diag_dump()` iterates token table entries and optionally listeners. `mptcp_diag_dump_listeners()` walks TCP listen hash buckets and maps MPTCP ULP listener subflows to MPTCP listener sockets. `mptcp_diag_get_info()` fills queue lengths and optional `mptcp_info`.

## Control Flow
Single lookup gets an MPTCP socket from the token table using `idiag_cookie[0]`, allocates a reply skb, fills inet diag data, and unicasts it. Dump iteration uses token iterator state stored in `cb->ctx`, filters by state, family, sport, and dport, and retries the same position if skb space runs out. Listener dumping walks listen buckets under RCU and bucket lock, filters MPTCP ULP sockets, references the owning MPTCP socket, and emits diag data. Init/exit register and unregister the handler.

## State and Persistence
The module owns only the registered handler. Dump cursors live in netlink callback context. Socket queue and MPTCP info are snapshots from live sockets.

## Dependencies and Integration Points
Depends on inet_diag, netlink diag sockets, MPTCP token table iteration, MPTCP listener/subflow context, and `mptcp_diag_fill_info()`. It complements `diag.c`, which adds per-subflow ULP details.

## Risks
Listener walking is lock-sensitive and must not hold stale references. Token iterator position correction on skb-full errors must remain correct to avoid skipped or duplicated sockets. Queue reporting overrides listener queues using the first TCP listener and must tolerate it being absent. The module alias encodes SOCK_DIAG protocol matching.

## Test Signals
Use `ss -M`, inet_diag dumps for established/listening MPTCP sockets, single lookup by token cookie, state/family/port filters, small skb dump continuation, CAP_NET_ADMIN info visibility, and module load/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/mptcp/mptcp_diag.c -->
