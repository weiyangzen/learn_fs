# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_span.c

## Purpose

`spectrum_span.c` implements mlxsw Spectrum SPAN and mirroring support. It allocates analyzer sessions, resolves mirror destinations, programs local and remote analyzer registers, tracks analyzed ports, binds mirroring triggers, and updates mirror configuration when bridge, VLAN, LAG, tunnel, or neighbor state changes. It supports physical-port mirrors, VLAN RSPAN, GRE tap IPv4/IPv6 mirrors when compiled in, and CPU-port mirroring on newer ASIC generations.

## Important APIs, Types, And Functions

`struct mlxsw_sp_span` owns the flexible array of `mlxsw_sp_span_entry` objects, trigger operation tables, entry operation tables, analyzed-port and trigger lists, policer base state, active-entry count, and respin work. `struct mlxsw_sp_span_entry_ops` abstracts destination types through `can_handle`, `parms_set`, `configure`, and `deconfigure`. `struct mlxsw_sp_span_trigger_ops` abstracts port triggers versus global drop/ECN triggers.

Public lifecycle functions are `mlxsw_sp_span_init()` and `mlxsw_sp_span_fini()`. Agent allocation uses `mlxsw_sp_span_agent_get()` and `mlxsw_sp_span_agent_put()`. Trigger binding uses `mlxsw_sp_span_agent_bind()` / `mlxsw_sp_span_agent_unbind()` and per-port enablement uses `mlxsw_sp_span_trigger_enable()` / `mlxsw_sp_span_trigger_disable()`. Analyzed egress ports are reference counted by `mlxsw_sp_span_analyzed_port_get()` and `mlxsw_sp_span_analyzed_port_put()`.

Destination-specific logic includes `mlxsw_sp_span_entry_phys_configure()`, VLAN RSPAN configuration, GRE tap route and neighbor resolution, bridge FDB/STP checks, LAG txable-member selection, and `mlxsw_sp_span_entry_unoffloadable()` fallback. ASIC-specific ops are exposed as `mlxsw_sp1_span_ops`, `mlxsw_sp2_span_ops`, and `mlxsw_sp3_span_ops`.

## Control Flow

Initialization validates `MAX_SPAN`, allocates the span object and session array, initializes lists/locks, calls the ASIC-specific init hook to install operation tables, registers devlink resource occupancy, and initializes respin work. Session creation selects an entry ops object by destination netdev, derives mirror parameters, applies optional policer base constraints, increments active count, and programs MPAT when the destination is offloadable. Existing sessions with identical destination, policer state, and session id are reused by refcount.

Remote tunnel mirror parameter derivation resolves a route, learns or creates a neighbor, walks VLAN, bridge, and LAG upper/lower devices, checks STP forwarding state, and either returns a concrete destination port plus L2/L3 encapsulation parameters or marks the session unoffloadable. `mlxsw_sp_span_respin_work()` later recomputes non-static parameters under RTNL and reprograms changed sessions.

Trigger binding first validates that the requested span id exists. Port ingress/egress triggers program MPAR immediately. Spectrum-2 global triggers program MPAGR and later toggle per-port traffic-class state through MOMTE. Unbind decrements trigger refs and calls the relevant unbind operation when the last user leaves.

## State And Persistence

State is in driver memory and hardware registers. Entries have refcounts, destination devices, hardware analyzer ids, current parameters, and operation tables. Analyzed ports are protected by `analyzed_ports_lock`; egress analyzed ports also allocate an internal mirror buffer by updating headroom configuration. Policer base state is shared across sessions and refcounted because hardware requires SPAN policers to live in a contiguous base range. Hardware state is MPAT, MPAR, MPAGR, MOMTE, MOGCR, and port headroom programming.

## Dependencies And Integration Points

The file depends on Linux bridge, VLAN, LAG, ARP/ND, IPv4/IPv6 GRE tunnel, RTNL, workqueue, and neighbor APIs. Internally it depends on `spectrum.h`, `spectrum_ipip.h`, `spectrum_router.h`, and `spectrum_switchdev.h`. Switchdev calls `mlxsw_sp_span_respin()` after bridge/FDB/VLAN changes so mirror tunnel destinations can be recomputed. Trap and sampling code use session ids that map to mirror-session trap ids.

## Risks And Edge Cases

Remote mirror offload is sensitive to changing routes, unresolved neighbors, bridge FDB placement, STP state, VLAN tagging, LAG carrier/txability, and cross-instance destination ports. Many unsupported cases intentionally degrade to unoffloaded SPAN instead of failing the session. Policer base handling can reject otherwise valid sessions when requested policers fall outside the already-programmed base range. Error paths around egress buffer enablement, MPAT programming, and trigger creation must keep refcounts and lists balanced. `mlxsw_sp_span_entry_invalidate()` deconfigures hardware and swaps to nop ops, so callers must not assume the original destination remains programmed.

## Test Signals

Useful tests include mirror to physical port, CPU port on Spectrum-2+, VLAN RSPAN, GRE tap IPv4/IPv6 offloadable and unoffloadable paths, bridge FDB and STP transitions followed by respin, LAG member carrier changes, trigger bind/unbind reference sharing, tail-drop/early-drop/ECN global trigger enable per traffic class, SPAN policer base conflicts, and cleanup warnings for leaked trigger or analyzed-port entries. No local executable tests were run for this research item.
