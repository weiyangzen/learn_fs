# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/nodemanager.h

## Purpose
`nodemanager.h` defines the in-kernel O2CB node and cluster structures plus lookup/dependency APIs used by heartbeat, networking, and quorum.

## Important APIs, types, and functions
`enum o2nm_fence_method` selects reset or panic self-fencing. `struct o2nm_node` stores configfs identity, name, node number, IPv4 address/port, IP tree node, local flag, and set-attribute bitmap. `struct o2nm_cluster` stores the config group, local-node state, node array, node bitmap, IP rbtree, network timeout tuning, and fence method. It declares lookup, reference, configured-map, current-node, and configfs dependency helpers.

## Control flow
Cluster subsystems call lookup helpers to convert node numbers/IPs into refcounted config items and call dependency helpers to pin configfs items while active operations depend on them.

## State and persistence behavior
The header defines runtime-only configfs-backed state. The node bitmap is used by heartbeat to decide which disk slots to read, and the fence method controls quorum self-fencing behavior.

## Dependencies and integration points
It includes the userspace ABI limits from `ocfs2_nodemanager.h`, configfs, and rbtree. It is included by heartbeat, quorum, TCP networking, and nodemanager implementation.

## Risks and test signals
Risks are direct structure coupling across cluster modules, singleton cluster assumptions via `o2nm_single_cluster`, and stale configfs references. Test signals include node lookup by number/IP, dependency pin/unpin under deletion, and fence-method use by quorum.
