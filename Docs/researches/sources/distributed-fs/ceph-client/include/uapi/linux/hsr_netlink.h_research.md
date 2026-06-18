<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsr_netlink.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/hsr_netlink.h

## Purpose
`hsr_netlink.h` defines netlink attributes for High-availability Seamless Redundancy and Parallel Redundancy Protocol network devices.

## Important APIs, types, and functions
The header exports generic-netlink node attributes `HSR_A_NODE_ADDR`, `HSR_A_IFINDEX`, `HSR_A_IF1_AGE`, `HSR_A_IF2_AGE`, `HSR_A_NODE_ADDR_B`, `HSR_A_IF1_SEQ`, `HSR_A_IF2_SEQ`, `HSR_A_IF1_IFINDEX`, `HSR_A_IF2_IFINDEX`, and `HSR_A_ADDR_B_IFINDEX`, bounded by `HSR_A_MAX`. Commands are `HSR_C_RING_ERROR`, `HSR_C_NODE_DOWN`, `HSR_C_GET_NODE_STATUS`, `HSR_C_SET_NODE_STATUS`, `HSR_C_GET_NODE_LIST`, and `HSR_C_SET_NODE_LIST`, bounded by `HSR_C_MAX`.

## Control flow
User space and the kernel exchange generic-netlink notifications and requests about HSR/PRP node status. Tools can request node status or node lists; the kernel can report ring errors or node-down events with node addresses, interface indexes, ages, and sequence numbers.

## State and persistence behavior
Runtime state lives in HSR/PRP node databases: node addresses, redundant-port ifindexes, per-port ages, and per-port sequence numbers. It persists until aged out, reconfigured, or the device/namespace is removed.

## Dependencies and integration points
It integrates with generic netlink, HSR/PRP network drivers, redundant Ethernet topologies, and network management tools that inspect node lists or receive topology events.

## Risks and test signals
Risks include wrong port ifindex attribution, node-table races, sequence number wrap handling, stale node ages, and netlink policy drift. Test signals include HSR/PRP device creation, dual-port failover, supervision frame observation, node-status/list dumps, sequence number validation, ring-error/node-down notifications, and invalid attribute rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/hsr_netlink.h -->
