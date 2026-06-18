# sources/distributed-fs/ceph-client/net/bridge/br_private_mrp.h

## Purpose
`br_private_mrp.h` defines bridge Media Redundancy Protocol state, software/hardware offload APIs, and on-wire MRP PDU header formats. MRP provides ring and interconnect redundancy distinct from STP.

## Important APIs, types, and functions
- `struct br_mrp` stores one MRP instance with primary/secondary/interconnect ports, ring/interconnect IDs, priorities, roles, states, transition counters, delayed test work, miss counters, monitoring flags, sequence IDs, and RCU destruction.
- `enum br_mrp_hw_support` expresses no support, software-assisted support, or full hardware support.
- Bridge MRP APIs include add/delete, port state/role changes, ring/interconnect state/role changes, and test start calls.
- Switchdev APIs let hardware add/delete MRP instances, set roles/states, and send ring/interconnect tests.
- PDU structs model TLV, common, ring-test, interconnect-test, OUI, and manufacture-data suboption headers.

## Control flow
MRP configuration comes through MRP netlink parsing declared in `br_private.h` and calls the APIs declared here. Runtime test delayed work sends/monitors MRP frames, updates miss counters, and changes ring/interconnect open state. Switchdev return values determine whether software continues protocol processing, assists hardware, or lets hardware own the protocol completely.

## State and persistence
MRP instances live in `br->mrp_list` under `CONFIG_BRIDGE_MRP`. Port pointers are RCU-protected; timers/delayed work drive transient test state. State is in-memory and disappears with the bridge or instance.

## Dependencies and integration points
The header depends on bridge internals and `<uapi/linux/mrp_bridge.h>`. It integrates with netlink `IFLA_BRIDGE_MRP`, switchdev offload, bridge port deletion, and STP exclusion: `br_stp_set_enabled()` rejects STP if MRP is already enabled.

## Risks and edge cases
MRP and STP control the same forwarding state and must not both own a bridge. Offload fallback must avoid duplicate software/hardware frame handling. Delayed work needs careful cancellation on instance deletion and port removal. Packed PDU structs must remain wire-compatible.

## Test signals
Test add/delete of rings and interconnects, role/state changes, test monitoring timeout/miss thresholds, switchdev support levels, port deletion, STP enable rejection while MRP exists, and PDU encode/decode interop.
