<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_netlink.h -->
# sources/distributed-fs/ceph-client/include/net/netdev_netlink.h

## Purpose
`netdev_netlink.h` defines the small per-netdev netlink socket binding container used by netdev netlink plumbing.

## Important APIs, types, and functions
It defines `struct netdev_nl_sock` with a mutex and list of bindings.

## Control flow
Netlink code serializes binding changes under `lock` and stores subscribed/bound objects in `bindings`.

## State and persistence
Runtime state is the binding list and its mutex. No persistent or global state is declared here.

## Dependencies and integration points
It depends on Linux list and mutex definitions through included headers. It integrates netdev-specific netlink binding state with the core netlink implementation.

## Risks and test signals
Risks include lock ordering with rtnl/netdev locks and list lifetime during socket teardown. Tests should cover bind/unbind, socket close, and concurrent notifications.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/netdev_netlink.h` completely for this pass (12 lines, 239 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/netdev_netlink.h -->
