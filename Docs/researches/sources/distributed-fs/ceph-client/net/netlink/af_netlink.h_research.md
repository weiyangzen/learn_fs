# sources/distributed-fs/ceph-client/net/netlink/af_netlink.h

## Purpose

`af_netlink.h` is the private header shared by the core netlink implementation and diagnostic helpers. It defines the in-kernel layout for netlink sockets and per-protocol netlink tables, along with flag IDs and group bitmap sizing helpers.

## Important APIs, Types, and Functions

The central type is `struct netlink_sock`, which embeds `struct sock` as its first member and adds netlink-specific state: flags, local and default destination port/group, subscription counts, group bitmap, maximum observed receive length, wait queue, bound/callback booleans, dump callback object, callback mutex, protocol callbacks, module owner, rhashtable node, and RCU head.

`nlk_sk()` converts from `struct sock *` to `struct netlink_sock *`, and `nlk_test_bit()` reads one of the private `NETLINK_F_*` flags. `struct netlink_table` describes one protocol number: its rhashtable, multicast listener list, RCU listener mask table, group count, callbacks, module, and registration count.

## Control Flow

The header has no executable control flow, but it fixes the object model used by `af_netlink.c` and `diag.c`. Creation initializes `netlink_sock` fields after `sk_alloc()`. Hash insertion uses `node`. Multicast operations use `groups` and `subscriptions`. Dump operations mutate `cb`, `cb_running`, `dump_done_errno`, and `nl_cb_mutex`.

## State and Persistence Behavior

All fields in `struct netlink_sock` are per-socket persistent state. `struct netlink_table` is global protocol persistent state referenced through exported `nl_table` under `nl_table_lock` plus RCU. The first-member embedding of `struct sock` is a hard ABI assumption for casting and allocation.

## Dependencies and Integration Points

The header depends on `linux/rhashtable.h`, `linux/atomic.h`, and `net/sock.h`. `diag.c` uses it to inspect private socket state. `af_netlink.c` owns allocation, synchronization, and mutation of these objects. Generic netlink also depends indirectly on the registered table callbacks stored here.

## Risks and Edge Cases

Changing field layout can break container casts, diagnostic assumptions, or BPF/proc observation. Adding flags requires keeping `NETLINK_F_*` numbering aligned with option handling and diagnostic flag export. Group bitmap sizing through `NLGRPSZ()` and `NLGRPLONGS()` must remain consistent with both allocation and user-visible group dumps.

## Test Signals

Build coverage of `af_netlink.c`, `diag.c`, and generic netlink is the primary signal. Runtime checks include successful `AF_NETLINK` socket creation, multicast group subscription, `/proc/net/netlink` output, and sock_diag reporting of flags/groups.
