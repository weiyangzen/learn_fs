<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/sysctl_net_unix.c -->
# sources/distributed-fs/ceph-client/net/unix/sysctl_net_unix.c

## Purpose
`sysctl_net_unix.c` registers the per-network-namespace sysctl interface for AF_UNIX. It exposes `net/unix/max_dgram_qlen`, the default datagram receive queue length limit used when new sockets are created.

## Important APIs, Types, and Functions
- `unix_table[]` defines the `max_dgram_qlen` sysctl entry with `0644` mode and `proc_dointvec`.
- `unix_sysctl_register()` installs the table for a net namespace, duplicating it for non-init namespaces so `.data` points to that namespace's `net->unx.sysctl_max_dgram_qlen`.
- `unix_sysctl_unregister()` unregisters the table and frees duplicated tables for non-init namespaces.

## Control Flow
`af_unix.c` initializes `net->unx.sysctl_max_dgram_qlen` to `10` and calls `unix_sysctl_register()` from pernet init. The sysctl handler then reads/writes the namespace-specific integer. Namespace exit unregisters and frees any duplicated table.

## State and Persistence
The sysctl value lives in `struct net`. The init namespace uses the static table directly; other namespaces allocate a copied `ctl_table`.

## Dependencies and Integration Points
It depends on sysctl infrastructure, net namespaces, and `af_unix.h`. `unix_create1()` reads the value to initialize `sk_max_ack_backlog` for new AF_UNIX sockets.

## Risks and Edge Cases
Registration failure must free duplicated tables. `unix_sysctl_unregister()` assumes `net->unx.ctl` is valid, matching the pernet init path that bails out on registration failure. There are no min/max bounds in the table, so extreme values depend on generic integer handling and downstream socket queue behavior.

## Test Signals
Create multiple net namespaces, set different `net.unix.max_dgram_qlen` values, create datagram sockets, and verify backlog/flow-control behavior differs by namespace. Exercise namespace teardown after sysctl writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/unix/sysctl_net_unix.c -->
