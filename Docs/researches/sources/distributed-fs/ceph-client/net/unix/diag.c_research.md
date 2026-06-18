<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/diag.c -->
# sources/distributed-fs/ceph-client/net/unix/diag.c

## Purpose
`diag.c` implements the AF_UNIX `SOCK_DIAG` netlink monitoring interface. It lets userspace dump or query Unix sockets and request optional name, VFS, peer, pending-connection, queue-length, memory, shutdown, and UID attributes.

## Important APIs, Types, and Functions
- Attribute dumpers include `sk_diag_dump_name()`, `sk_diag_dump_vfs()`, `sk_diag_dump_peer()`, `sk_diag_dump_icons()`, `sk_diag_show_rqlen()`, and `sk_diag_dump_uid()`.
- `sk_diag_fill()` builds one `unix_diag_msg` netlink response and attaches requested attributes.
- `unix_diag_dump()` iterates all per-net AF_UNIX hash buckets for dump requests.
- `unix_lookup_by_ino()` and `unix_diag_get_exact()` support exact inode lookup and retry with larger skb sizes.
- `unix_diag_handler_dump()` dispatches dump versus exact query.
- `unix_diag_init()` and `unix_diag_exit()` register/unregister the sock_diag handler.

## Control Flow
Userspace sends `SOCK_DIAG_BY_FAMILY` for `AF_UNIX`. Dump requests iterate bucket/slot positions saved in netlink callback args and call `sk_diag_fill()` for matching socket states. Exact requests require `udiag_ino`, look up a socket by inode, validate the cookie, allocate a reply, retry with more attribute space if needed, and unicast the result.

## State and Persistence
The module stores only the registered `sock_diag_handler`. It reads live socket state from AF_UNIX hash tables, peer pointers, VFS path data, receive queues, and queue length helpers.

## Dependencies and Integration Points
It depends on AF_UNIX internals from `af_unix.h`, sock_diag, netlink, user namespace UID munging, TCP socket state values, and `unix_inq_len()`/`unix_outq_len()` from `af_unix.c`.

## Risks and Edge Cases
Attribute dumping must respect locking: name may be read under hash lock via acquire semantics, VFS path requires state lock, listener icons require receive queue lock, and peer lookup must hold a reference. Exact lookup scans all buckets and can race close, so cookie checks and references are important. Netlink response sizing is conservative but bounded by a page.

## Test Signals
Use `ss -x`, `ss -xl`, and direct unix_diag netlink tests against sockets in each state, with abstract/pathname names, listener queues, peers, SCM queues, namespaces, and exact inode/cookie queries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/diag.c -->
