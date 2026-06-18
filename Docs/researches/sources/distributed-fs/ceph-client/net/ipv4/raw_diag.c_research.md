# sources/distributed-fs/ceph-client/net/ipv4/raw_diag.c

## Purpose
Adds SOCK_DIAG/INET_DIAG support for raw sockets, allowing netlink dump/query/queue inspection and optional destruction of IPv4 and IPv6 raw sockets.

## Important APIs, types, and functions
`raw_get_hashinfo()` selects IPv4 or IPv6 hash tables. `raw_lookup()` matches by raw protocol and diag id fields. `raw_sock_get()` finds and references a socket. `raw_diag_dump_one()` handles single requests. `raw_diag_dump()` streams sockets. `raw_diag_get_info()` fills queue sizes. Optional `raw_diag_destroy()` aborts sockets. `raw_diag_handler` registers with inet_diag.

## Control flow
Single lookup scans raw buckets under RCU and increments socket refcount before reply fill. Dumping resumes from `cb->args`, filters namespace, family, pseudo-ports, optional bytecode, and calls `inet_sk_diag_fill()`. Init registers the handler; exit unregisters it.

## State and persistence
No owned socket state. It reads raw hash tables from `raw.c` and `rawv6`, uses netlink callback args as cursors, and holds temporary socket refs while building replies.

## Dependencies and integration points
Integrates with `NETLINK_SOCK_DIAG`, inet_diag, raw IPv4/IPv6 hash tables, raw match helpers, netlink capability checks, and optional diag destroy. Compile-time checks keep `inet_diag_req_v2` and `inet_diag_req_raw` layout-compatible.

## Risks
Dump cursor correctness and socket refcounting are key. The ABI compatibility mapping of `pad` to `sdiag_raw_protocol` is layout-sensitive. Capability checks gate detailed exposure. Destroy must avoid racing teardown.

## Test signals
Dump IPv4/IPv6 raw sockets, query by protocol/address/interface, apply bytecode filters, validate queue sizes, compare admin/non-admin details, test dump continuation with many sockets, and destroy sockets when enabled.
