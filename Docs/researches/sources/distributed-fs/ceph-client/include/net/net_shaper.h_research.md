<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_shaper.h -->
# sources/distributed-fs/ceph-client/include/net/net_shaper.h

## Purpose
`net_shaper.h` defines the kernel-facing representation and driver operations for hardware traffic shapers managed through the net shaper UAPI.

## Important APIs, types, and functions
It defines binding types, `struct net_shaper_binding`, `struct net_shaper_handle`, `struct net_shaper`, and `struct net_shaper_ops` with `group`, `set`, `delete`, and `capabilities` callbacks.

## Control flow
The networking core serializes operations per device, tracks user-applied shaper configuration, calls driver `set` or `delete` for individual nodes, `group` to nest queue leaves under a scheduling node, and `capabilities` to report supported scopes/features.

## State and persistence
Runtime state is shaper handle/scope/id, parent linkage, rate/burst/priority/weight parameters, leaf counts for node scopes, and RCU lifetime. Device implementations mirror that state in NIC hardware.

## Dependencies and integration points
It depends on UAPI `net_shaper.h`, netdevice/devlink forward declarations, netlink extack, and optional device locking in `netdev_lock.h`. It integrates traffic shaping with netdevices and future devlink ports.

## Risks and test signals
Risks include unsupported nesting, handle uniqueness bugs, stale RCU shaper nodes, ambiguity between zero and unset values, and driver/core state divergence after partial failures. Tests should cover capabilities, set/delete, group creation, extack errors, queue-scope limits, and concurrent queue reconfiguration.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/net_shaper.h` completely for this pass (120 lines, 3571 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/net_shaper.h -->
