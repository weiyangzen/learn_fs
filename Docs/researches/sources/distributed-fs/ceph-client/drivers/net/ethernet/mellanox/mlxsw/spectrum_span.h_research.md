# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_span.h

## Purpose

`spectrum_span.h` is the public internal interface for mlxsw Spectrum SPAN/mirroring. It defines the session, trigger, and operation contracts consumed by switchdev, qdisc/sample, trap, and ASIC-selection code.

## Important APIs, Types, And Functions

`enum mlxsw_sp_span_session_id` assigns logical CPU mirror sessions for buffer-drop and sampling use and reserves up to eight ids that correspond to hardware mirror-session trap ids. `struct mlxsw_sp_span_parms` carries resolved mirror destination details: destination port, TTL, source/destination MACs, source/destination L3 addresses, VLAN id, policer id, policer enable flag, and session id. `enum mlxsw_sp_span_trigger` names ingress, egress, tail-drop, early-drop, and ECN triggers. `struct mlxsw_sp_span_trigger_parms` carries a span id plus sampling probability rate.

The exported API covers span lifecycle, respin scheduling, entry lookup/invalidation, agent get/put, analyzed-port reference management, trigger bind/unbind, trigger enable/disable, and ingress/egress classification through `mlxsw_sp_span_trigger_is_ingress()`. `struct mlxsw_sp_span_ops` exposes ASIC-specific initialization and policer-base programming hooks.

## Control Flow

Callers allocate a SPAN agent by providing a destination device and optional policer/session attributes. The implementation resolves these into `struct mlxsw_sp_span_parms`, returns a span id, and later uses that id in trigger binding. Triggers can then be enabled per port and traffic class when needed. Network topology changes call `mlxsw_sp_span_respin()` so dynamic mirror destinations can be recomputed.

## State And Persistence

The header-level state contract is reference-counted: `struct mlxsw_sp_span_entry` contains a refcount, current parameters, operation table, destination device, and hardware id. Persistence is in memory and in hardware analyzer/trap configuration programmed by the implementation. There is no filesystem state.

## Dependencies And Integration Points

The header depends on Linux Ethernet address types, refcounting, and `spectrum_router.h` for `union mlxsw_sp_l3addr`. It exports `mlxsw_sp1_span_ops`, `mlxsw_sp2_span_ops`, and `mlxsw_sp3_span_ops` for ASIC dispatch from the core Spectrum initialization path.

## Risks And Edge Cases

Session ids are not arbitrary; changing their order or count can break the mirror-session trap-id mapping. Callers must pair every `agent_get` with `agent_put`, every bind with unbind, and analyzed-port get with put. `dest_port == NULL` means unoffloaded SPAN, not necessarily an allocation failure.

## Test Signals

Compile coverage should catch API drift between `spectrum_span.c` and callers. Runtime tests should verify reference pairing, trigger direction classification, CPU/session id mapping, and ASIC-specific ops selection. No local executable tests were run for this research item.
