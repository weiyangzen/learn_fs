# subset-b-004565 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.h

## Purpose

`spectrum_router.h` is the internal router subsystem interface for the mlxsw Spectrum driver. It exposes the in-memory router object, route interface (RIF), neighbor, nexthop, IP-in-IP, bridge/router replay, and counter entry points used by switchdev, tunnel, trap, and port code. The header does not implement behavior, but it defines the shared contracts that let other mlxsw files interact with the L3 hardware offload layer without depending on private router implementation details.

## Important APIs, Types, And Functions

`struct mlxsw_sp_router` is the central state holder. It contains hash tables for router interfaces, neighbors, nexthop groups, and nexthops; a `gen_pool` and RIF array for RIF index allocation; IDR and atomic counters for RIF MAC profiles; virtual-router and LPM tree state for IPv4/IPv6; delayed works for neighbor refresh, unresolved nexthop probing, and nexthop group activity; notifier blocks for FIB, nexthop, netevent, address, and netdevice changes; arrays of RIF and IPIP operation tables; NVE decap configuration; a mutex for shared router resources; and adjacency-related capabilities.

`struct mlxsw_sp_router_nve_decap` records the configured underlay table, tunnel index, underlay protocol, source address, and valid bit for NVE decapsulation. `struct mlxsw_sp_rif_ipip_lb_config` describes loopback IPIP RIF type, key, underlay protocol, and source address. `enum mlxsw_sp_rif_counter_dir` distinguishes ingress and egress RIF counters.

The exported function declarations cover RIF lookup and device association (`mlxsw_sp_rif_by_index()`, `mlxsw_sp_rif_dev_ifindex()`, `mlxsw_sp_rif_dev_is()`), RIF counters, neighbor iteration and counters, IPIP tunnel update/demotion, nexthop iteration and adjacency/counter updates, ECN initialization, bridge VLAN-to-router replay, LAG router replay, and netdevice enslavement/deslavement replay.

## Control Flow

The header describes a router subsystem driven by kernel notifiers and explicit replay helpers. Address/FIB/nexthop/netdevice events update the router's hash tables and delayed work queues. Other subsystems ask the router for RIF, neighbor, and nexthop state when programming FDB entries, SPAN tunnel paths, bridge VLANs, or LAG changes. IPIP tunnel changes go through update and demotion helpers that can recreate loopback RIFs, preserve encapsulation state, and update nexthops.

## State And Persistence

All persistence is runtime driver state and hardware programming. `struct mlxsw_sp_router` owns allocator state, hash tables, delayed work, notifier registrations, reference/counter fields, and hardware index values such as `adj_trap_index`. There is no disk persistence. The mutex documents that shared router resources require serialization, while several counters use atomics and refcounts to coordinate concurrent notification paths.

## Dependencies And Integration Points

The header depends on `spectrum.h`, `reg.h`, Linux networking device types, rhashtable, IDR, gen_pool, delayed work, notifiers, and mlxsw L3 address/protocol definitions. It integrates with switchdev bridge code via `mlxsw_sp_router_bridge_vlan_add()` and bridge/LAG replay helpers, with SPAN GRE resolution through `mlxsw_sp_l3addr` and router underlay helpers, and with tunnel/NVE code through IPIP and NVE decap structures.

## Risks And Edge Cases

The router state spans asynchronous notifier callbacks and delayed workers, so lifetime and lock ordering are critical. RIF index allocation deliberately offsets gen_pool allocations because `gen_pool_alloc()` returns zero on failure; code that bypasses the offset can confuse index zero with allocation failure. IPIP demotion by source address can affect multiple tunnels and must preserve the `except` tunnel. LPM trees, nexthop groups, and neighbor counters are shared resources whose reference counts must remain balanced through replay and rollback paths.

## Test Signals

Useful signals include bridge VLAN RIF creation/removal, LAG join/leave with existing router interfaces, IPv4/IPv6 neighbor add/delete and counter updates, nexthop group activity, IPIP tunnel creation and demotion, NVE decap programming, FIB notifier replay after device enslave/deslave, and cleanup of delayed works/notifier registrations. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_router.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_span.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_span.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_span.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_span.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.c

## Purpose

`spectrum_switchdev.c` is the mlxsw Spectrum bridge, FDB, MDB, VLAN, and VXLAN switchdev offload implementation. It translates Linux bridge and switchdev events into hardware FIDs, flood tables, learning state, STP state, multicast database entries, static/dynamic FDB records, and NVE/VXLAN mappings. It is the main L2 integration point between netdevice topology and Spectrum hardware forwarding.

## Important APIs, Types, And Functions

`struct mlxsw_sp_bridge` owns global bridge state, FDB notification delayed work, ageing time, a single VLAN-aware bridge guard, bridge-device list, MID bitmap, and per-ASIC bridge ops. `struct mlxsw_sp_bridge_device` mirrors a Linux bridge and tracks bridge ports, MDB list/rhashtable, VLAN-awareness, multicast state, router state, and ops. `struct mlxsw_sp_bridge_port` mirrors a bridge member with refcount, STP state, flags, mrouter state, and either LAG id or system port. `struct mlxsw_sp_bridge_vlan` groups port VLANs per bridge port.

Public entry points include `mlxsw_sp_switchdev_init()`, `mlxsw_sp_switchdev_fini()`, `mlxsw_sp_port_bridge_join()`, `mlxsw_sp_port_bridge_leave()`, `mlxsw_sp_bridge_vxlan_join()`, `mlxsw_sp_bridge_vxlan_leave()`, `mlxsw_sp_bridge_device_is_offloaded()`, `mlxsw_sp_rif_fdb_op()`, and `mlxsw_sp_bridge_port_stp_state()`. Internal ops implement 802.1Q, 802.1D, and 802.1AD bridge behavior, including Spectrum-2 egress ethertype differences.

## Control Flow

Initialization allocates `mlxsw_sp_bridge`, installs bridge ops, sets default FDB ageing time, registers switchdev notifiers, and initializes FDB notification work. Bridge join obtains or creates a bridge device and bridge port, calls the bridge type's `port_join`, replays router/netdevice enslavement, and unwinds in reverse on failure. VLAN-aware bridges replay switchdev VLAN objects; VLAN-unaware bridges attach a default or VLAN-upper VID to an 802.1D FID. 802.1AD joins additionally change VLAN classification and, on Spectrum-2, egress ethertype.

VLAN add creates or finds a port VLAN, programs VLAN membership/PVID, obtains the bridge FID, sets UC/MC/BC flood membership, maps port/VID to FID, sets learning and STP, and links the port VLAN into the bridge VLAN list. VLAN delete reverses this, flushes FDB and MDB state as needed, unmaps the FID, and releases bridge-port references.

FDB programming uses SFD register records for port, LAG, router, and tunnel entries. Hardware FDB notifications are polled by delayed work using SFN queries, converted to bridge/VXLAN switchdev notifications, and reprogrammed as dynamic entries. Static FDB events from switchdev are deferred to workqueues and either program local/LAG entries or tunnel entries. VXLAN events translate Linux VXLAN FDB records to NVE flood IPs or tunnel unicast entries and report offload state back to switchdev.

MDB handling allocates MID/PGT entries, tracks member and mrouter ports with refcounts, writes multicast SFD records when multicast snooping is enabled, and updates mrouter inclusion when bridge or port mrouter attributes change.

## State And Persistence

State is in memory plus hardware forwarding tables. The bridge object stores live bridge devices, bridge ports, VLAN groupings, MDB hash/list state, pending FDB notification work, and ageing time. Hardware persistence includes FID allocations and VNI bindings, flood table membership, STP and learning bits per VID, PGT/MID multicast groups, SFD FDB/MDB records, NVE IPv6 KVDL mappings, and VXLAN offload state. Notifier work items hold device references with `netdev_hold()` until processed.

## Dependencies And Integration Points

The file depends on Linux switchdev, bridge, VLAN, VXLAN, workqueue, RTNL, and netdevice APIs. Internally it integrates with Spectrum FID management, NVE/VXLAN helpers, router RIF replay, LAG helpers, SPAN respin, port VLAN state, flood table programming, PGT/MID allocation, and hardware register packing in `reg.h`.

## Risks And Edge Cases

Only one VLAN-aware bridge is supported; attempts to create another fail. VLAN filtering and protocol cannot be changed after a bridge is offloaded. Locked bridge-port flags are rejected on VLAN uppers or ports with VLAN uppers. Error unwinds must reverse partially programmed FID flood state, learning/STP state, PVID changes, switchdev replay, NVE bindings, and MDB mrouter additions. Dynamic FDB notifications may refer to invalid ports or stale FIDs; the code removes unprocessable entries to stop repeated notifications. VXLAN support rejects non-default remote port/VNI, remote interface, multicast MAC, and multicast destination IP. Hardware has one FDB while Linux has bridge and VXLAN FDBs, so tunnel FDB programming depends on matching bridge FDB ownership.

## Test Signals

Useful tests include 802.1D, 802.1Q, and 802.1AD bridge joins/leaves; VLAN add/delete with PVID and untagged changes; LAG bridge membership replay; STP, learning, flooding, locked, MAB, and mrouter attributes; bridge ageing bounds; MDB add/delete and multicast-snooping toggles; dynamic FDB learning/ageing from hardware notifications; static FDB add/delete; VXLAN bridge join/leave and VLAN-to-VNI remap; VXLAN FDB add/delete/offload notifications; and failure injection for FID, PGT, SFD, switchdev replay, and NVE operations. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.h

## Purpose

`spectrum_switchdev.h` is a narrow internal header exposing bridge-port lookup and STP-state query helpers to other mlxsw Spectrum files, especially SPAN destination resolution.

## Important APIs, Types, And Functions

The file forward-declares `struct mlxsw_sp_bridge` and `struct mlxsw_sp_bridge_port`. `mlxsw_sp_bridge_port_find()` locates the offloaded bridge-port object for a given bridge member netdevice. `mlxsw_sp_bridge_port_stp_state()` returns the cached STP state from that bridge-port object.

## Control Flow

Callers use these helpers after they have a Spectrum bridge object and a candidate bridge member device. SPAN uses this to verify that a bridge FDB-selected egress port is in a forwarding state before offloading remote mirroring.

## State And Persistence

The header exposes read-only access to switchdev state held in `spectrum_switchdev.c`. It does not allocate or persist state itself.

## Dependencies And Integration Points

The only direct include is `<linux/netdevice.h>`. The integration point is intentionally small to avoid exposing the full bridge data model to unrelated subsystems.

## Risks And Edge Cases

Callers must handle `NULL` from `mlxsw_sp_bridge_port_find()` because bridge devices can be absent, not offloaded, or in transition. The returned pointer is meaningful only under the synchronization assumptions of the caller, normally RTNL.

## Test Signals

Compile-time usage should remain limited. Runtime signals are SPAN remote mirror offload through bridge destinations and STP transitions that cause mirror respin to enable or disable offloadability. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_switchdev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.c

## Purpose

`spectrum_trap.c` implements devlink trap, trap group, trap policer, and RX listener support for mlxsw Spectrum. It maps hardware trap ids and mirror reasons to devlink-visible traps, registers core listeners, reports trapped/dropped/sampled packets to devlink and psample, programs trap groups and policers in hardware, and provides ASIC-specific trap additions.

## Important APIs, Types, And Functions

`struct mlxsw_sp_trap_policer_item`, `struct mlxsw_sp_trap_group_item`, and `struct mlxsw_sp_trap_item` extend devlink policer/group/trap definitions with hardware ids, priorities, fixed-policer flags, listener arrays, and source-trap markers. The common arrays define policers, groups, and a large table of L2/L3/tunnel/ACL/control traps. ASIC-specific arrays add Spectrum-1 ACL sampling and Spectrum-2 buffer drop/source sampling behavior.

RX listener functions include normal packet delivery with or without offload marks, L3 mark delivery, drop reporting, ACL drop reporting with flow action cookies, PTP delivery, and psample sampling for ingress, egress, and policy-engine sources. Public devlink callbacks include `mlxsw_sp_devlink_traps_init()`, `mlxsw_sp_devlink_traps_fini()`, `mlxsw_sp_trap_init()`, `mlxsw_sp_trap_fini()`, `mlxsw_sp_trap_action_set()`, `mlxsw_sp_trap_group_init()`, `mlxsw_sp_trap_group_set()`, `mlxsw_sp_trap_policer_init()`, `mlxsw_sp_trap_policer_fini()`, `mlxsw_sp_trap_policer_set()`, `mlxsw_sp_trap_policer_counter_get()`, and `mlxsw_sp_trap_group_policer_hw_id_get()`.

## Control Flow

Initialization first reserves and programs a thin CPU policer for the dummy group, initializes that dummy group, builds the policer item array from predefined policers plus dynamically generated extras, registers all policers with devlink, builds common plus ASIC-specific group arrays and registers them, then builds common plus ASIC-specific trap arrays and registers them. Failure unwinds registered objects in reverse order.

When devlink initializes a trap, `mlxsw_sp_trap_init()` looks up the trap item and registers each valid hardware listener with mlxsw core. Trap fini unregisters in reverse listener order. Trap action changes reject source traps and otherwise toggle listener state for DROP versus TRAP actions. Trap group init/set programs HTGT with the selected hardware group id, optional hardware policer id, and configured priority; fixed-policer groups reject policer rebinding.

Packet listeners first associate the skb with the mlxsw port, update per-CPU rx stats, derive the protocol, then either report and consume dropped packets, deliver packets to GRO, mark offloaded packets, invoke PTP receive handling, or sample through psample with metadata from RX mirror metadata.

## State And Persistence

State lives in `mlxsw_sp->trap`: registered policer/group/trap arrays, counts, thin policer hardware id, max policer count, and policer usage bitmap. Hardware state includes QPCR policer programming, HTGT trap group programming, and core trap listener state. Packet statistics are updated in per-port per-CPU counters. There is no disk persistence.

## Dependencies And Integration Points

The file depends on devlink traps, mlxsw core listener registration, register packing for QPCR/HTGT, skb RX metadata, ACL action cookie lookup, PTP receive handling, psample, sampling trigger parameter lookup, port devlink-port lookup, and Spectrum ASIC trap ops from `spectrum_trap.h`.

## Risks And Edge Cases

Listener arrays have a fixed maximum of three entries; adding traps with more hardware reasons requires increasing the limit and auditing loops. Source traps cannot have their action changed because they are controlled by the source subsystem. Policer burst sizes must be powers of two. The thin policer consumes a hardware policer before devlink policers are registered, so available-policer accounting must include reserved bits. Drop listeners push the Ethernet header before devlink reporting and must consume skbs on all paths. Sample metadata depends on RX metadata validity for Tx port, congestion, TC, and latency fields.

## Test Signals

Useful tests include devlink trap list/group/policer registration, trap action changes, rejection of source-trap action changes, fixed-policer rebinding rejection, policer rate/burst programming and counter reads, packet delivery with offload marks, ACL drop cookies, PTP traps, psample ingress/egress/ACL samples, and fault injection through registration and hardware write failures. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.h

## Purpose

`spectrum_trap.h` defines the Spectrum-specific trap subsystem state and ASIC operation hooks used by `spectrum_trap.c` and core Spectrum initialization.

## Important APIs, Types, And Functions

`struct mlxsw_sp_trap` stores arrays of trap policer, group, and trap items; their counts; the reserved thin policer hardware id; the maximum number of hardware policers; and a flexible policer usage bitmap. `struct mlxsw_sp_trap_ops` lets each ASIC generation return additional group and trap item arrays through `groups_init` and `traps_init`.

The header exports `mlxsw_sp1_trap_ops` and `mlxsw_sp2_trap_ops`. Spectrum-1 and Spectrum-2 share the common trap table from the C file but differ in sampling and buffer-drop trap capabilities.

## Control Flow

Core initialization allocates `struct mlxsw_sp_trap` with enough bitmap storage for supported policers, assigns the appropriate `trap_ops`, and lets `spectrum_trap.c` concatenate common and ASIC-specific arrays during devlink trap initialization.

## State And Persistence

State is runtime-only and belongs to the driver instance. The flexible bitmap tracks hardware policer allocation across the reserved dummy policer and devlink-visible policers.

## Dependencies And Integration Points

The header includes Linux list and devlink headers and forward-relies on item structures defined privately in `spectrum_trap.c`. It is integrated with devlink callbacks in the mlxsw core driver ops.

## Risks And Edge Cases

The flexible bitmap must be allocated with enough trailing storage for `max_policers`; undersized allocation would corrupt memory. ASIC ops must provide arrays whose lifetime outlives initialization because the C file copies them immediately but relies on accurate counts.

## Test Signals

Compile coverage should catch mismatches between ops and implementation. Runtime signals are correct trap sets for Spectrum-1 versus Spectrum-2 and correct policer bitmap accounting during init/fini. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/spectrum_trap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/trap.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/trap.h

## Purpose

`trap.h` defines numeric mlxsw hardware trap identifiers for packet traps and asynchronous event traps. These constants are the stable bridge between register/listener programming and higher-level Spectrum trap handling.

## Important APIs, Types, And Functions

The first anonymous enum lists packet trap ids, covering Ethernet control and FDB events, L2 protocols, multicast snooping, sampling, router exceptions, IPv6 control traffic, tunnel decap and NVE ARP, BFD/router alert, discard reasons, ACL traps, and mirror-session trap ids `MLXSW_TRAP_ID_MIRROR_SESSION0` through `MLXSW_TRAP_ID_MIRROR_SESSION7`. `MLXSW_TRAP_ID_MAX` caps packet trap ids at `0x3FF`.

`enum mlxsw_event_trap_id` lists firmware and hardware event ids such as fatal events, port up/down, module plug/unplug, temperature warning, PTP FIFO events, downstream device status, binary code transfer completion, and port mapping changes.

## Control Flow

There is no executable control flow. Other files compile these constants into listener tables and register payloads. For example, `spectrum_trap.c` uses many ids in listener macros, and `spectrum_span.h` documents that SPAN session ids correspond to the mirror-session trap ids in this header.

## State And Persistence

The file defines constants only. The persistence concern is ABI-like stability relative to firmware/hardware trap numbering and devlink trap mapping.

## Dependencies And Integration Points

It has no includes and is consumed by mlxsw core and Spectrum trap/listener code. The constants must match firmware register definitions and register-packing helpers in `reg.h`.

## Risks And Edge Cases

Renumbering or reusing ids would break hardware event interpretation. Mirror-session ids must remain contiguous if session-id arithmetic is used elsewhere. Adding new traps requires matching listener, devlink trap, documentation, and hardware support updates.

## Test Signals

Compile tests catch missing enum names. Runtime signals include successful trap listener registration, expected devlink trap reporting, SPAN mirror-session trap delivery, and correct hardware event dispatch. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/trap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/txheader.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/txheader.h

## Purpose

`txheader.h` defines mlxsw transmit-header field accessors and constants. The transmit header is prepended to packets sent from the host CPU to the switch ASIC and tells hardware whether a packet is control or data, which port or multicast id to use, whether FID forwarding lookup is valid, and which protocol/type fields apply.

## Important APIs, Types, And Functions

The file uses `MLXSW_ITEM32` macros to define bitfield accessors for version, control/data type, protocol, router-origin flag, FID-valid flag, switch partition id, control traffic class, destination port/MID, FID, and packet type. Constants define header length (`MLXSW_TXHDR_LEN`), supported versions, Ethernet control/data values, Ethernet protocol value, traffic-class enum values, receive descriptor queue ids, CPU signature values, EMAD marker values, and data/control type values.

## Control Flow

There is no runtime control flow in this header. Tx paths allocate or access a 16-byte header and use the generated accessors to pack fields before sending packets to the ASIC.

## State And Persistence

The header defines packet metadata layout only. State exists transiently in skb/headroom buffers and hardware interpretation of each transmitted packet.

## Dependencies And Integration Points

It depends on the mlxsw item macro infrastructure, usually available from register/header packing includes. It integrates with EMAD/control packet paths, data packet injection, L2 forwarding through FID lookup, and CPU-port transmission.

## Risks And Edge Cases

Bit offsets and constants must match the ASIC transmit-header format exactly. Data packets and control packets use different semantics for destination fields; setting `fid_valid`, `port_mid`, or `type` incorrectly can misdirect traffic. Version and protocol fields have fixed required values.

## Test Signals

Useful tests are packet injection through control and data paths, EMAD operation, CPU-to-port transmission, FID-valid forwarding, and hardware drops caused by malformed tx headers. Static build coverage should catch missing accessor macro definitions. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/txheader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Kconfig

## Purpose

`meta/Kconfig` introduces the Meta Platforms Ethernet vendor menu and the `FBNIC` driver configuration option for the Meta Host Network Interface.

## Important APIs, Types, And Functions

`config NET_VENDOR_META` is a boolean vendor gate, defaulting to `y`, that controls whether Meta device questions are shown. `config FBNIC` is a tristate driver option with architecture and feature dependencies: 64-bit or compile-test, not S390, `MAX_SKB_FRAGS < 22`, PCI MSI, and optional PTP clock support. It selects devlink, page pool, XPCS PCS, phylink, and PLDM firmware support.

## Control Flow

Kconfig evaluation first decides whether the Meta vendor submenu is active. If active, the user can build `FBNIC` built-in or as module. The selected dependencies influence which kernel subsystems are enabled and whether the Makefile descends into `meta/fbnic/`.

## State And Persistence

Kconfig state is persisted in the kernel build configuration, not at runtime. Selecting `FBNIC=m` produces an `fbnic` module; selecting `y` links it built-in.

## Dependencies And Integration Points

The option integrates with PCI/MSI, PTP, devlink, page-pool RX allocation, PCS_XPCS, phylink, and PLDM firmware infrastructure. The dependency on `MAX_SKB_FRAGS < 22` documents a driver/hardware limit relevant to skb fragment handling.

## Risks And Edge Cases

Changing dependencies can expose the driver on unsupported architectures or without required interrupt/firmware/link-management subsystems. The vendor gate does not disable already-selected objects directly; it hides questions, matching normal kernel vendor menu behavior.

## Test Signals

Build tests should cover `FBNIC=y`, `FBNIC=m`, and `COMPILE_TEST` configurations, dependency rejection on S390 or too-large `MAX_SKB_FRAGS`, and module naming as `fbnic`. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Makefile

## Purpose

`meta/Makefile` connects the Meta Ethernet vendor directory to the kernel build system.

## Important APIs, Types, And Functions

The file contains one build rule: `obj-$(CONFIG_FBNIC) += fbnic/`. When `CONFIG_FBNIC` is enabled, kbuild descends into the `fbnic` subdirectory.

## Control Flow

Kbuild evaluates `CONFIG_FBNIC`; if disabled, no objects from this vendor directory are built. If enabled as built-in or module, the subdirectory Makefile decides the actual object list and module composition.

## State And Persistence

There is no runtime state. Build state is determined by the kernel `.config`.

## Dependencies And Integration Points

This Makefile depends on the `FBNIC` Kconfig option and the existence of `meta/fbnic/Makefile`. It integrates into the broader `drivers/net/ethernet` vendor build structure.

## Risks And Edge Cases

The directory is built only when `CONFIG_FBNIC` is set. Renaming the option or subdirectory without updating this line breaks driver inclusion.

## Test Signals

Build tests should verify that `CONFIG_FBNIC=m` creates the fbnic module and `CONFIG_FBNIC=n` skips the directory. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/Makefile

## Purpose

`meta/fbnic/Makefile` defines the fbnic module object composition for the Meta Host Network Interface driver.

## Important APIs, Types, And Functions

`obj-$(CONFIG_FBNIC) += fbnic.o` creates the driver object or module. `fbnic-y` lists component objects: CSR access/tests, debugfs, devlink, ethtool, firmware, firmware log, hardware stats, hwmon, IRQ, MAC, netdev, PCI, phylink, RPC, MDIO, time/PTP, TLV, and TX/RX logic.

## Control Flow

Kbuild links the listed `fbnic-y` objects into `fbnic.o` when `CONFIG_FBNIC` is enabled. The ordering mostly follows subsystem dependencies, with low-level CSR and support code listed before bus/netdev data-path pieces.

## State And Persistence

There is no runtime state in the Makefile. Build output persists as a built-in object or module artifact according to kernel configuration.

## Dependencies And Integration Points

The object list maps directly to driver subsystem files and must stay synchronized with declarations in `fbnic.h` and related headers. It integrates with the parent `meta/Makefile`.

## Risks And Edge Cases

Missing a required object produces unresolved symbols; keeping an obsolete object produces build failures. The trailing continuation before the comment must remain syntactically valid for kbuild.

## Test Signals

Build tests for built-in and module configurations are the main signal. Linker errors indicate missing object membership or stale prototypes. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic.h

## Purpose

`fbnic.h` is the central internal header for the Meta fbnic Ethernet driver. It defines the main device object, low-level CSR and firmware access helpers, interrupt/vector constants, driver-wide prototypes, self-test result codes, and board metadata used by the fbnic component files.

## Important APIs, Types, And Functions

`struct fbnic_dev` is the primary device state. It holds Linux device and netdev pointers, debugfs/hwmon/devlink health objects, mapped CSR bases for host and firmware windows, MAC ops, MSI-X vector metadata, NAPI IRQ names, service work, firmware mailboxes and completion slots, firmware capabilities, heartbeat state, PCI tuning values, local TCAM and MAC/IP address mirrors, queue limits, PTP clock state and time lock, PMD state, hardware stats, firmware time/log state, MDIO bus, and power-save timeout.

Inline helpers include `fbnic_present()` for CSR availability, `fbnic_wr32()`, `fbnic_rd32()`, `fbnic_wrfl()`, `fbnic_rmw32()`, firmware CSR accessors, `fbnic_bmc_present()`, and `fbnic_init_failure()`. The header declares devlink, firmware mailbox, hwmon, MAC IRQ, NAPI IRQ, generic IRQ allocation, MSI-X self-test, debugfs, RPC reset, MDIO creation, CSR register dump/test helpers, coalescing configuration, and driver board info.

## Control Flow

Driver components include this header to operate on `struct fbnic_dev`. PCI probing allocates it through devlink helpers, maps CSR regions, initializes firmware/mailbox, IRQs, netdev, phylink/MAC, stats, and time support. Runtime register access goes through `rd32`/`wr32` wrappers that tolerate absent hardware by checking `uc_addr0` for writes and using the out-of-line read helper for reads.

## State And Persistence

Persistent runtime state is concentrated in `struct fbnic_dev`. It mirrors hardware TCAM, MAC/IP filters, queue capacity, firmware state, PTP timekeeping, PMD training status, statistics, MDIO, and service work. There is no disk persistence; state is rebuilt across probe/reset. `time_lock` serializes PTP time CSR machinery, while `fw_tx_lock` serializes firmware mailbox Tx queue access.

## Dependencies And Integration Points

The header depends on Linux interrupt, MMIO, PTP, workqueue, netdevice, PCI, MDIO, devlink, hwmon, and fbnic subsystem headers for CSR, firmware, logs, stats, MAC, and RPC. It is the integration surface across all fbnic source objects listed in the Makefile.

## Risks And Edge Cases

CSR access can occur while the device is removed or reset; `fbnic_present()` and guarded writes reduce but do not remove lifetime concerns. The fixed `FBNIC_MAX_NAPI_VECTORS` and mailbox completion slot counts must match hardware and IRQ allocation. Local TCAM mirrors must stay synchronized with firmware/hardware RPC programming. Timekeeping fields require correct locking to avoid inconsistent high/offset reads. Init-failure logic treats missing netdev as a special state used by cleanup paths.

## Test Signals

Useful tests include probe/remove, reset during register access, firmware mailbox traffic, devlink health reporting, IRQ allocation/free and MSI-X self-test codes, PTP clock operations, MDIO creation, TCAM programming, debugfs and hwmon registration, and netdev open/close. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.c

## Purpose

`fbnic_csr.c` implements fbnic CSR register dumping and register self-test logic. It provides ethtool/debug style register snapshots across normal CSR sections and RPC RAM, calculates dump length, and validates selected queue registers by writing known patterns and checking writable/read-only bit behavior.

## Important APIs, Types, And Functions

`struct fbnic_csr_bounds` describes start/end register ranges. `fbnic_csr_sects[]` lists CSR sections to dump, including interrupt, queue manager, TCE, TMI, PTP, RXB, RPC, fabric, master, PCS, RSFEC, MAC, signal, PCIe, PUL, queue, and RPC RAM. `fbnic_csr_get_regs()` writes a version and a sequence of section start/end markers plus register values into a caller-supplied buffer. `fbnic_csr_regs_len()` returns the expected u32 count including two marker words per section.

`fbnic_csr_get_regs_rpc_ram()` handles RPC RAM specially because it is not linearly dumped; it iterates TCAM action, MACDA, outer/inner IP source/destination tables, and RSS table entries through indexed register macros. `struct fbnic_csr_reg_test_data` and `pattern_test[]` define queue register self-test targets, strides, array lengths, readable masks, and writable masks. `fbnic_csr_regs_test()` runs the pattern test across all described queue instances.

## Control Flow

Register dumping skips the final RPC_RAM section in the linear loop, dumps all ordinary sections by reading every CSR between start and end, then appends the special RPC_RAM dump. A `WARN_ON` verifies that the number of u32s written matches `fbnic_csr_regs_len()`.

The self-test loops over each register descriptor and each array index, computes the actual register address from base plus stride, writes patterns `~0`, `0x5A5A5A5A`, `0xA5A5A5A5`, and `0`, masks expected values by readable/writable masks, reads back, logs an error on mismatch, and returns the failing register number. Success returns `FBNIC_REG_TEST_SUCCESS`.

## State And Persistence

The file does not own persistent state. It reads and writes hardware CSRs through the `fbnic_dev` accessors. The self-test intentionally mutates queue-related registers and is documented for offline use where reset after test can restore device state.

## Dependencies And Integration Points

It depends on `fbnic.h` for accessors and device logging, and on generated CSR macros from `fbnic_csr.h`. It integrates with ethtool register dump and driver self-test paths declared in `fbnic.h`.

## Risks And Edge Cases

The dump length must stay synchronized with section bounds and RPC RAM table dimensions; mismatches trigger `WARN_ON` and can corrupt caller expectations. RPC RAM table constants duplicate hardware dimensions and must track CSR macro definitions. The register self-test writes to hardware and should only run when the interface is offline and reset afterward. A failure on register offset zero would be ambiguous with success, but the code documents that such a register is not included.

## Test Signals

Useful tests include ethtool register dump length/version validation, RPC RAM dump coverage, self-test success on known-good offline hardware, intentional fault or mask mismatch detection, and ensuring reset restores queue registers after test. No local executable tests were run for this research item.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/meta/fbnic/fbnic_csr.c -->
