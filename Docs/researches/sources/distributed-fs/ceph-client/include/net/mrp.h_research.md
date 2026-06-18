<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mrp.h -->
# sources/distributed-fs/ceph-client/include/net/mrp.h

## Purpose
`mrp.h` defines the Multiple Registration Protocol core data structures for applicants, applications, attributes, vector attribute parsing, and join/leave API used by MRP applications such as MVRP.

## Important APIs, types, and functions
Key types are PDU/message/vector headers, `struct mrp_skb_cb`, applicant/event/action enums, `struct mrp_attr`, `struct mrp_application`, `struct mrp_applicant`, and `struct mrp_port`. Functions register/unregister applications, init/uninit applicants, and request join/leave for attributes.

## Control flow
Applications register a packet type, multicast group address, version, and max attribute count. Per-device applicants keep timers, queues, current PDU, and an RB tree of MAD attributes. Join/leave requests update applicant state and enqueue PDUs; received vector events are decoded through skb control-block metadata.

## State and persistence
Runtime state includes per-port RCU applicant pointers, applicant timers, spinlock-protected queues and RB tree, active flag, current PDU, and per-attribute applicant state. No disk persistence exists.

## Dependencies and integration points
It depends on netdevice, skb, packet_type, timers, RB trees, spinlocks, and RCU. It integrates MRP applications with Ethernet multicast registration.

## Risks and test signals
Risks include skb control-block size assumptions, timer teardown races, RB tree duplicate handling, vector length/flag decoding, application unregister while applicants are active, and max attribute enforcement. Tests should cover register/unregister, per-device init/uninit, join/leave transitions, vector event decoding, timer-driven TX, and RCU teardown.

## Source read
Read `sources/distributed-fs/ceph-client/include/net/mrp.h` completely for this pass (148 lines, 3200 bytes).
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/mrp.h -->
