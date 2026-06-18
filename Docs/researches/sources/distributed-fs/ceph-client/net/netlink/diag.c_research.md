# sources/distributed-fs/ceph-client/net/netlink/diag.c

## Purpose

`diag.c` implements the `sock_diag` handler for `AF_NETLINK`. It lets userspace dump netlink sockets, their protocol, state, port IDs, multicast memberships, memory information, flags, inode, and socket cookie.

## Important APIs, Types, and Functions

`sk_diag_fill()` builds one `SOCK_DIAG_BY_FAMILY` reply containing `struct netlink_diag_msg`. Optional attributes come from `sk_diag_dump_groups()`, `sock_diag_put_meminfo()`, and `sk_diag_put_flags()`. `__netlink_diag_dump()` walks one netlink protocol table, first through its rhashtable and then through multicast-only sockets in `mc_list`. `netlink_diag_dump()` handles either a single protocol or `NDIAG_PROTO_ALL`. `netlink_diag_handler_dump()` validates requests and starts a dump through `netlink_dump_start()`.

## Control Flow

A sock_diag request reaches `netlink_diag_handler_dump()`. Only dump requests are supported; non-dump requests return `-EOPNOTSUPP`. For each selected protocol, `__netlink_diag_dump()` creates or reuses an rhashtable iterator in `cb->args[2]`, emits matching sockets in the caller's network namespace, exits that walk, and then scans `mc_list` for bound but unhashed multicast sockets. Iteration positions are persisted in `cb->args[0]` and `cb->args[1]` across dump calls.

## State and Persistence Behavior

The module does not own long-lived socket state. It reads `struct netlink_sock` state from `af_netlink.h` and stores temporary dump cursor state in `netlink_callback` arguments. `netlink_diag_dump_done()` exits any active hash walk and frees the iterator.

## Dependencies and Integration Points

The file integrates with `sock_diag_register()`, `netlink_dump_start()`, rhashtable walking, `nl_table`, `nl_table_lock`, and netlink private socket layout. The module alias advertises diagnostic support for `PF_NETLINK`, `NETLINK_SOCK_DIAG`, and `AF_NETLINK`.

## Risks and Edge Cases

The two-phase walk is easy to break: rhashtable iterators must be exited exactly once, and `mc_list` must be protected by `nl_table_lock`. Namespace filtering avoids leaking sockets across namespaces. Optional attributes can overrun the skb; callers signal partial progress by returning `skb->len` so the dump can continue.

## Test Signals

Run `ss -A netlink`, `ss -a -f netlink`, or sock_diag-based tests while sockets are bound to groups and while a dump callback is running. Verify `NDIAG_SHOW_GROUPS`, `NDIAG_SHOW_MEMINFO`, and `NDIAG_SHOW_FLAGS` attributes and module load/unload behavior.
