# sources/distributed-fs/ceph-client/include/uapi/linux/mrp_bridge.h

## Purpose
Defines bridge Media Redundancy Protocol constants and enums for ring/interconnect roles, states, port states/roles, TLV headers, and sub-TLV headers.

## Important APIs, Types, And Functions
Exports frame/domain/version/prio constants and enums `br_mrp_ring_role_type`, `br_mrp_in_role_type`, `br_mrp_ring_state_type`, `br_mrp_in_state_type`, `br_mrp_port_state_type`, `br_mrp_port_role_type`, `br_mrp_tlv_header_type`, and `br_mrp_sub_tlv_header_type`.

## Control Flow
Bridge MRP code and userspace configure roles and states, then encode/decode MRP Ethernet TLVs according to these numeric values.

## State, Persistence, And Dependencies
State persists in bridge MRP instance configuration and received/transmitted protocol frames. Depends on `linux/types.h` and `linux/if_ether.h`.

## Integration Points
Used by bridge netlink MRP configuration and industrial Ethernet redundancy control planes.

## Risks
Protocol numeric values are wire-visible. Inconsistent role/state handling can block or forward ports incorrectly in a redundancy ring.

## Test Signals
Validate netlink role/state round trips, TLV type encoding, max frame length, port state transitions, and interoperability with MRP peers.
