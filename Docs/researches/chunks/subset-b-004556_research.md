# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/reg.h lines 1-8858

## Scope

This chunk covers the first 8,858 lines of `reg.h`, the main Mellanox `mlxsw` hardware register layout header. It starts with the register descriptor infrastructure and covers switch, bridge/FDB, VLAN, LAG, policy engine, QoS, port, trap, and the first router register families. The chunk ends inside the `RIGR2` multicast router interface group register; the rest of `RIGR2` and later management, tunnel, shared-buffer, and event registers continue in later chunks.

The file is a hardware ABI map. It does not implement device algorithms directly. It declares register IDs and lengths, generates bitfield accessors through `MLXSW_ITEM*` macros, and provides small `static inline` helpers that pack or unpack command payloads for firmware register transactions.

## Purpose

`reg.h` is the central schema for the `mlxsw` register protocol. Each `MLXSW_REG_DEFINE(name, id, len)` creates a `struct mlxsw_reg_info` instance with the firmware register ID, payload length, and symbolic name. Callers use `MLXSW_REG(name)`, `MLXSW_REG_LEN(name)`, and `MLXSW_REG_ZERO(name, payload)` when allocating and issuing register payloads through the core `mlxsw` register query/write path.

The chunk's inline helpers encode common register transactions:

- Switch and bridge programming: base MAC, system-port mapping, FDB edits and notifications, VLAN membership, spanning tree state, FID allocation, flood tables, multicast IDs, and NVE/VXLAN bridge mappings.
- LAG programming: LAG descriptor creation/destruction, distributor membership, collector state, and global hash configuration.
- Policy engine and ACL programming: TCAM allocation, ACL and ACL-group binding, rule copy/move, flexible actions, C-TCAM/A-TCAM rule programming, eRP tables, bloom filter entries, and infrastructure entry deletion.
- QoS and buffer programming: trust state, policers, DSCP/priority mappings, ETS hierarchy, shapers, WRED/ECN profiles, PFC, port priority-to-buffer maps, and per-port buffer thresholds.
- Port and module programming: port-to-module/lane mapping, MTU, speed/autonegotiation, MAC address, admin state, counters, flow control, module state, diagnostics, loopback, EEPROM override, label-port mapping, and module type.
- Trap and router programming: trap groups and trap IDs, router enablement, RIFs, router TCAM allocation, adjacency entries, router counters, algorithmic LPM trees/routes/hosts, host-table dumps, ECMP update, tunnel decapsulation, IPv6-address storage, and adjacency activity dumps.

## Register Infrastructure

The shared register infrastructure appears at the top of the chunk. `struct mlxsw_reg_info` carries the firmware register ID, length in bytes, and text name. `MLXSW_REG_DEFINE()` materializes a constant descriptor named `mlxsw_reg_<name>`. The payload helpers then rely on generated setters/getters from `item.h`:

- `MLXSW_ITEM32`, `MLXSW_ITEM16`, `MLXSW_ITEM8`, and `MLXSW_ITEM64` define scalar fields inside the byte payload.
- `MLXSW_ITEM_BUF` and indexed variants define memcpy accessors for byte arrays such as MAC addresses, IPv6 addresses, TCAM keys, masks, and action sets.
- `MLXSW_ITEM_BIT_ARRAY` defines dense indexed bit arrays, for example VLAN spanning tree states, multicast port membership, eRP vectors, and activity vectors.
- `MLXSW_ITEM32_LP` is used throughout for local-port fields and depends on `port.h` local-port encoding conventions.

The pack helpers nearly always zero the entire register payload first, then set only index, operation, and data fields required by the command. Callers can still set additional fields after the helper returns; many consumers do this for optional counters, flooding metadata, action sets, or hardware-generation-specific fields.

## Switch, Bridge, VLAN, FDB, and Multicast Registers

The first block covers core switch and bridge state:

- `SGCR`, `SPAD`, `SSPR`, and `SFDAT` configure global switch state: LAG PGT lookup base, switch physical base MAC, local-port to system-port mapping, and FDB aging time.
- `SFD` is the FDB write/query register. It supports dump/query/query-and-clear operations and write test/edit/remove operations. Records can be unicast, unicast LAG, multicast, or unicast tunnel. Helpers such as `mlxsw_reg_sfd_uc_pack()`, `mlxsw_reg_sfd_uc_lag_pack()`, `mlxsw_reg_sfd_mc_pack()`, `mlxsw_reg_sfd_uc_tunnel_pack4()`, and `mlxsw_reg_sfd_uc_tunnel_pack6()` build records and update `num_rec` when a higher record index is packed.
- `SFN` is the FDB notification poll register. `mlxsw_reg_sfn_pack()` requests up to 64 records. Unpack helpers decode learned/aged MAC entries for regular ports, LAGs, and tunnel entries.
- `SPMS`, `SPVID`, `SPVM`, `SPAFT`, `SPVTR`, `SVPE`, `SPVC`, `SPEVET`, `SMPE`, and `SPVMLR` cover spanning tree state, PVID, VLAN membership, ingress frame admittance, VLAN stacking, virtual-port mode, VLAN EtherType classification, egress VLAN EtherType selection, multicast egress VID mapping, and per-port/per-VID learning.
- `SFGC`, `SFDF`, `SFMR`, `SFFP`, `SVFA`, `SMID2`, and `SPFSR` cover bridge/FID lifecycle: flood table selection, FDB flush, FID create/destroy, NVE/CFF flooding profiles, VID/VNI to FID mapping, multicast replication lists, and port security.

The FDB and notification path has stateful control flow in hardware. FDB dumps use a `record_locator` cursor. SFN polling returns a variable number of learned or aged-out records. SFD write responses can return fewer records than requested; consumers in `spectrum_switchdev.c` check `num_rec` after writes. Static/dynamic policy, activity bits, and tunnel protocol fields are persisted in hardware FDB state rather than in this header.

## LAG Registers

`SLDR`, `SLCR`, and `SLCOR` define the LAG programming surface:

- `SLDR` creates/destroys a LAG descriptor and adds/removes system ports from its distributor list.
- `SLCR` configures global LAG hashing. The chunk defines a large set of `MLXSW_REG_SLCR_LAG_HASH_*` bit flags for ingress port, MACs, EtherType, VLAN ID, IP addresses, L4 ports, protocol, IPv6 flow label, FCoE IDs, and RoCE destination QP.
- `SLCOR` controls the collector side of local-port LAG membership and includes helpers for add, remove, enable, and disable.

One visible risk is that `mlxsw_reg_slcor_col_disable_pack()` sets `MLXSW_REG_SLCOR_COL_LAG_COLLECTOR_ENABLED` instead of `MLXSW_REG_SLCOR_COL_LAG_COLLECTOR_DISABLED`. If this exact source is used unchanged, LAG collector disable operations can be encoded incorrectly. This should be reconciled against upstream or existing tests before changing behavior.

## Policy Engine and ACL Registers

The policy-engine section is the most structurally dense part of the chunk:

- `PGCR` configures the default action pointer base.
- `PPBT`, `PACL`, and `PAGT` bind ingress/egress ACL groups to ports, make ACL regions valid, and describe ordered ACL groups.
- `PTAR` allocates, resizes, tests, or frees TCAM regions and returns or consumes an opaque `tcam_region_info` buffer. Flexible key IDs can be appended for up to 16 key encodings.
- `PPRR` describes L4 port range comparators.
- `PPBS` maps policy-based switching table entries to destination system ports.
- `PRCR` moves or copies rule ranges between TCAM regions.
- `PEFA` stores flexible action sets in KVD linear space and exposes an activity bit with optional clear-on-read behavior.
- `PEMRBT` binds multicast-router protocol handling to an ACL group on newer hardware.
- `PTCE2` programs C-TCAM rules with valid bit, operation, priority, region info, key, mask, and flexible action set.
- `PERPT`, `PERAR`, `PTCE3`, `PERCR`, `PERERP`, and `PEABFE` add the Spectrum-2 A-TCAM/eRP path: eRP table rows, hardware region association, A-TCAM rule entries, region masks and prune behavior, eRP vector binding, and bloom filter entry state.
- `IEDR` deletes infrastructure entries by resource type, size, and start index; deleting nonexistent entries is documented as a good flow.

These registers integrate with `spectrum_acl_tcam.c`, `spectrum_acl_ctcam.c`, `spectrum_acl_atcam.c`, `spectrum_acl_erp.c`, `spectrum_acl_bloom_filter.c`, `spectrum_acl_flex_actions.c`, and `spectrum2_kvdl.c`. The important persistent state is in hardware TCAM, KVD linear memory, ACL IDs/groups, eRP banks, bloom filters, and action-set storage. Opaque region handles are copied through payload buffers and must remain byte-exact.

## QoS, Policing, WRED, and Buffer Registers

QoS-related registers in this chunk cover both packet classification and scheduling:

- `QPTS`, `QPDP`, `QPDPM`, `QPDSM`, `QTCT`, `QTCTM`, and `QRWE` configure trust state, default priority, DSCP-to-priority, priority-to-DSCP, priority-to-traffic-class, multicast-aware TC mapping, and PCP/DSCP rewrite enablement.
- `QPCR` configures policers. It defines global versus flow policers, rate units, byte/packet mode, committed information rate, committed burst size, clear-counter behavior, violate count, and actions such as discard or changing priority/color.
- `QEEC` configures ETS hierarchy elements, DWRR, min/max shapers, PTP shaper mode, packet/byte mode, and burst-size limits.
- `QPSC` configures Spectrum-1 PTP shaper timing and timestamp increments.
- `CWTP` and `CWTPM` configure WRED/ECN profiles per port/traffic class and map TCP/non-TCP green/yellow/red traffic to profiles.
- `PFCC`, `PPTB`, and `PBMC` connect QoS to flow control and buffers: pause/PFC policies, switch priority to buffer assignment, lossy/lossless buffer size, xoff/xon thresholds, and pause timing.
- `PPCNT` exposes many per-port counter groups, including IEEE/RFC Ethernet counters, discard counters, per-priority counters, per-TC counters, WRED discard, and ECN-marked counters.

Consumers include DCB, qdisc, policer, trap policer, buffer, ethtool, and core port-stat paths. Test signals should include both configuration readback and live traffic counters: DSCP rewrite, PFC pause counters, WRED discard/ECN counters, policer violation counters, and TC queue depths.

## Port, Module, and Diagnostics Registers

The port section defines the hardware-facing lifecycle for front-panel ports:

- `PMLP` maps local ports to slot/module/lane tuples and controls width and separate Rx/Tx lane interpretation. It is used by minimal and Spectrum port discovery and split/unsplit handling.
- `PMTU`, `PTYS`, `PPAD`, and `PAOS` cover MTU, Ethernet speed/autonegotiation, per-port or base MAC address, and administrative/operational port state. `PTYS` includes both legacy and extended Ethernet speed masks up to 800G.
- `PSPA` associates a local port with a switch partition.
- `PMAOS`, `PMPE`, `PMTDB`, `PMECR`, `PMMP`, `PLLP`, and `PMTM` handle module reset/admin state, plug/unplug events, possible module-to-local-port mappings, mapping-change event configuration, EEPROM override properties, label-port mapping, and module type.
- `PPLR` sets PHY local loopback.
- `PDDR` queries PHY troubleshooting pages through the diagnostics database.

Persistent state lives in firmware port configuration, module state, mapping tables, and event arming. Several registers have write-enable bits (`ase`, `ee`, `pte`, mapping event enable fields) that intentionally preserve unrelated hardware state unless explicitly set.

## Trap and CPU Delivery Registers

`HTGT` and `HPKT` configure CPU delivery:

- `HTGT` defines trap groups, optional policer IDs, mirror action, trap priority, CPU traffic class, and RDQ selection.
- `HPKT` maps individual trap IDs to actions and trap groups, with optional control-buffer handling.

Core code and Spectrum trap code use these definitions to register listeners, default trap groups, per-group policers, and enabled/disabled trap actions. Incorrect trap group/action encoding can make control protocols disappear, flood the CPU, or bypass intended policers.

## Router, RIF, LPM, Host, Adjacency, and Tunnel Registers

The router section begins with global router enablement and then builds the forwarding tables:

- `RGCR` enables IPv4/IPv6 routing, sets max router interfaces, controls priority rewrite behavior, and can disable route/host activity-bit updates.
- `RITR` creates, deletes, and configures router interfaces. It supports VLAN, FID, sub-port, and loopback RIF types. Helpers pack base RIF state, MAC addresses, counters, sub-port binding, VLAN/FID binding, and IPv4/IPv6 IP-in-IP loopback parameters.
- `RTAR` and `RRCR` allocate and move/copy router TCAM rules for multicast route tables.
- `RATR` programs adjacency entries in linear/KVD space, including Ethernet next-hop MACs, IP-in-IP underlay destination pointers, trap actions, egress RIF, and flow counters. `RATRAD` dumps and clears adjacency activity for ECMP groups.
- `RDPM` maps routed DSCP values to switch priority.
- `RICNT` reads or clears router-interface counters.
- `RALTA`, `RALST`, and `RALTB` allocate algorithmic LPM trees, define sorted prefix-bin tree structure, and bind trees to virtual-router/protocol tuples.
- `RALUE` programs LPM unicast route entries, including IPv4/IPv6 prefixes, operation/update masks, marker/route entry types, best-match prefix length, remote/local/IP2ME actions, ECMP pointers, local eRIFs, tunnel decap pointers, and activity bits.
- `RAUHT` programs exact host entries for IPv4/IPv6 neighbors, including RIF, destination IP, MAC, trap action, counters, and activity bits.
- `RALEU` bulk-updates ECMP pointer and size for all matching route entries in a virtual-router/protocol tuple.
- `RAUHTD` dumps and optionally clears active host entries. IPv4 records contain up to four entries per record; IPv6 records use one full record.
- `RTDP` configures NVE and IP-in-IP decapsulation properties, including tunnel index, egress RIF, overlay ingress RIF, SIP checks, type checks, GRE key checks, and expected GRE key.
- `RIPS` stores IPv6 addresses in KVD linear space for tunnel and FDB references.
- The chunk starts `RIGR2`, defining the multicast egress-interface group register ID, KVD index, next-list pointer, RMID pointer, and the beginning of valid eRIF entries. The rest of the eRIF list layout and helpers continue after the chunk boundary.

This router section integrates heavily with `spectrum_router.c`, `spectrum_ipip.c`, `spectrum_nve_vxlan.c`, and multicast-router TCAM code. Hardware state includes virtual routers, RIF indices, LPM trees, route entries, neighbor/host entries, adjacency groups, KVD tunnel pointers, counters, and activity bits. Many operations are stateful: allocation returns implicit hardware resources, activity dump operations clear bits, invalidated adjacency entries may not be immediately reusable, and route updates can use masks to update only selected fields.

## Control Flow and State Behavior

The C control flow in this chunk is intentionally small and mostly follows these patterns:

- Zero the whole payload with `MLXSW_REG_ZERO()`.
- Set index and operation fields first.
- Set data fields for the specific helper.
- For bulk records, read the current `num_rec` or `size` and increase it if the caller packs a higher index.
- For unpack helpers, copy hardware-owned fields out of response payloads into caller-provided variables or buffers.

There is no heap allocation, locking, persistence to disk, or asynchronous execution in this header. Persistence is entirely in the device and firmware tables programmed by the generated payloads. Fields marked `Index`, `OP`, `RW`, `RO`, or `WO` document how firmware interprets payload bytes for get/set operations, and callers must sequence commands according to those semantics.

State-sensitive behavior visible in this chunk includes FDB dump cursors, FDB notification polling sessions, TCAM region handles, ACL activity bits, PEFA/PTCE activity clear-on-read, policer and counter clear bits, port/module event arming, router and host activity bits, RAUHTD dump sessions, and adjacency invalidation/reuse timing.

## Dependencies and Integration Points

Direct dependencies are Linux kernel headers plus local `item.h` and `port.h`. The chunk assumes the generated accessors handle byte order, bit shifts, indexed record offsets, and buffer copies consistently with the firmware command ABI.

Important source-tree consumers include:

- `core.c`, `core_env.c`, and `minimal.c` for trap setup, module handling, and minimal port discovery.
- `spectrum.c`, `spectrum_ethtool.c`, `spectrum_dcb.c`, `spectrum_buffers.c`, `spectrum_qdisc.c`, `spectrum_policer.c`, `spectrum_trap.c`, and `spectrum_ptp.c` for port, QoS, counter, trap, buffer, and PTP flows.
- `spectrum_switchdev.c`, `spectrum_fid.c`, `spectrum_pgt.c`, `spectrum_nve.c`, and `spectrum_nve_vxlan.c` for bridge, FDB, VLAN, FID, multicast, and VXLAN/NVE flows.
- `spectrum_acl_*`, `spectrum1_acl_tcam.c`, `spectrum2_acl_tcam.c`, `spectrum2_kvdl.c`, and multicast-router TCAM code for ACL, TCAM, KVDL, eRP, and bloom-filter programming.
- `spectrum_router.c`, `spectrum_ipip.c`, and `spectrum_router.h` for RIFs, LPM routes, host entries, ECMP, adjacency tables, IP-in-IP, and NVE decapsulation.

## Risks

- Register ABI drift is high impact. Wrong IDs, lengths, offsets, or bit widths can corrupt unrelated firmware fields or make commands fail.
- Bulk-record helpers do not enforce all maximum counts. Some helpers warn, but most rely on callers to stay within `*_REC_MAX_COUNT` and valid index ranges.
- Many fields share offsets depending on record type or action type. Setting fields for the wrong SFD, RATR, RALUE, or RTDP variant can encode invalid mixed records.
- Activity bits and clear-on-read operations can lose diagnostic or aging information if used accidentally.
- Opaque TCAM region info and KVD pointers must be copied byte-exactly. Treating them as typed integers outside their documented fields can break ACL, tunnel, and adjacency lifetimes.
- Port/module update-enable bits protect unrelated state. Forgetting them can make writes ineffective; setting them too broadly can overwrite event or admin state.
- Router invalidation and adjacency reuse have firmware timing constraints. Reusing invalidated RATR entries immediately can return transient failures.
- Local-port, system-port, LAG ID, FID, RIF, KVD, PGT, and virtual-router spaces overlap conceptually but are distinct hardware namespaces.
- The apparent `SLCOR` disable helper encoding should be checked, because it sets the collector-enabled enum in a function named disable.
- The chunk ends mid-`RIGR2`, so a complete per-file report must merge this with the following chunk before describing multicast eRIF group helpers as complete.

## Test and Validation Signals

Useful validation signals are mostly integration and hardware-facing:

- Kernel build coverage for all `mlxsw_reg_*` generated accessors and inline helpers.
- Switchdev bridge tests for VLAN membership, PVID, STP state, FDB add/remove, learning and aging notifications, multicast DB entries, VXLAN FDB entries, and FDB flushes.
- LAG tests for create/destroy, add/remove member, collector enable/disable, traffic hashing, and link transitions.
- ACL tests for region allocation/free, ACL group binding, rule add/delete/update, counter/action activity, C-TCAM resize/move, A-TCAM eRP/bloom-filter paths, and KVDL cleanup.
- QoS tests for DSCP/PCP trust, rewrite, ETS, qdisc offload, policer drops, WRED/ECN marking, PFC pause behavior, and per-TC/per-priority counters.
- Port tests for speed/autonegotiation, MTU, admin/oper state, MAC programming, module plug/unplug events, split/unsplit lane mapping, loopback, and ethtool statistics.
- Trap tests for trap group policers, trap actions, event delivery, control-buffer use, and CPU traffic class/RDQ routing.
- Router tests for RIF creation/deletion, RIF counters, IPv4/IPv6 route add/update/delete, ECMP changes, neighbor host table programming, adjacency activity, IP2ME, NVE/IP-in-IP decap, IPv6 KVD address storage, and RAUHTD dump-and-clear behavior.
