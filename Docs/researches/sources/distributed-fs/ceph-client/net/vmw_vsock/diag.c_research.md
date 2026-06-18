# sources/distributed-fs/ceph-client/net/vmw_vsock/diag.c

## Purpose
`diag.c` implements the `sock_diag` interface for AF_VSOCK. It allows userspace tools such as `ss -A vsock` to dump open vsock sockets, their state, addresses, shutdown state, inode, and socket cookie.

## Important APIs, Types, And Functions
The main functions are `sk_diag_fill()`, `vsock_diag_dump()`, and `vsock_diag_handler_dump()`. The registered handler is `vsock_diag_handler` for family `AF_VSOCK`. It emits `struct vsock_diag_msg` replies in `SOCK_DIAG_BY_FAMILY` netlink messages and consumes `struct vsock_diag_req`.

## Control Flow
Initialization registers the sock_diag handler. A dump request with `NLM_F_DUMP` starts a netlink dump using `vsock_diag_dump()`. The dump walks first the bind table, then the connected table, using `cb->args[]` to persist table, bucket, and index across multipart netlink calls. It filters sockets by network namespace and requested state mask, skips connected-table sockets already seen in the bound table, and fills each matching record without taking `sk_lock` because `vsock_table_lock` pins list membership and lock ordering forbids nesting in the opposite direction.

## State And Persistence
The module owns no socket state. It reads the global vsock tables under `vsock_table_lock`. Netlink callback state persists only across a single multipart dump in `cb->args`.

## Dependencies And Integration Points
The file integrates with `af_vsock.c` exported tables and `vsock_table_lock`, the sock_diag netlink subsystem, network namespaces, and `uapi/linux/vm_sockets_diag.h`. It is enabled by `CONFIG_VSOCKETS_DIAG` and built as `vsock_diag`.

## Risks And Edge Cases
The main risks are duplicate reporting between bound and connected tables and lock-order violations. The implementation avoids duplicates for sockets present in both tables and intentionally reads fields locklessly while the global table lock keeps the socket alive. Very large socket sets depend on correct `cb->args` resume bookkeeping.

## Test Signals
Useful tests include `ss -A vsock` across listening, connecting, connected, and closed states; namespace filtering; state-mask filtering; multipart dumps with many sockets; module load/unload; and lockdep validation while sockets are concurrently connecting and closing.
