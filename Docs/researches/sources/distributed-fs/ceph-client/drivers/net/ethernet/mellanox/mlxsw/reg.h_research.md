# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/reg.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004556`: lines 1-8858, `Docs/researches/chunks/subset-b-004556_research.md`
- `subset-b-004557`: lines 8859-13211, `Docs/researches/chunks/subset-b-004557_research.md`

## Chunk Research

### subset-b-004556: lines 1-8858

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

### subset-b-004557: lines 8859-13211

# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlxsw/reg.h lines 8859-13211

Chunk ID: `subset-b-004557`

## Scope and Purpose

This chunk is the final large register-definition span of Mellanox/NVIDIA `mlxsw`'s `reg.h`. It covers the tail of router register support, most management and monitoring register definitions, tunnel register definitions for NVE and IP-in-IP, shared-buffer registers, the global register-info lookup table, and the PUDE port up/down event layout.

The code is not an executing driver module by itself. It is a declarative register contract: each `MLXSW_REG_DEFINE()` declares a hardware/firmware register ID and payload length, `MLXSW_ITEM*()` macros describe bit fields and buffers inside that payload, and small `static inline` pack/unpack helpers zero and populate command payloads before the core register transport submits them. The surrounding mlxsw driver layers use these definitions to configure routing, multicast, monitoring, firmware update, device management, tunneling, shared buffers, and event decoding.

## Important APIs, Types, and Functions

- Router tail definitions include `rigr2`, `recr2`, `rmft2`, and `reiv`. `mlxsw_reg_rigr2_pack()` and `mlxsw_reg_rigr2_erif_entry_pack()` build router interface group records; `mlxsw_reg_recr2_pack()` initializes ECMP hash configuration; `mlxsw_reg_rmft2_ipv4_pack()` and `mlxsw_reg_rmft2_ipv6_pack()` program multicast forwarding TCAM entries; `mlxsw_reg_reiv_pack()` selects the egress-RIF/port-page key for egress VID mapping.
- ECMP hash enums define outer and inner header layers and fields used by `recr2`, including IPv4/IPv6 source/destination fields, protocol/next-header, flow label, and TCP/UDP ports. Callers set bit arrays after `mlxsw_reg_recr2_pack()` to choose the exact hash key.
- Fan and thermal registers include `mfcr`, `mfsc`, `mfsm`, `mfsl`, `fore`, `mtcap`, `mtmp`, `mtwe`, and `mtbr`. They expose PWM frequency/active masks, duty cycle, tachometer RPM and thresholds, fan-under-limit events, sensor count, per-sensor temperature/max/threshold data, warning bitmaps, and bulk temperature records. `MLXSW_REG_MTMP_TEMP_TO_MC()` converts signed 0.125-degree units into millidegrees Celsius.
- Module EEPROM and status access is defined by `mcia` and `mcion`. `mlxsw_reg_mcia_pack()` selects slot, module, page, device offset, size, and I2C address for SFP/QSFP/CMIS EEPROM reads. Constants encode page lengths, low/high I2C addresses, flat-memory handling, threshold page offsets, and module ID/revision values. `mlxsw_reg_mcion_pack()` selects a module for presence and low-power status bits.
- Port analyzer and sampling registers include `mpat`, `mpar`, `mpsc`, `mgpc`, `mprs`, `mogcr`, `mpagr`, and `momte`. These cover mirror-session destinations and encapsulations, per-port ingress/egress mirroring, packet sampling rate, general-purpose counters, parser depth and VXLAN UDP port, global PTP/mirroring policer configuration, global mirror-trigger mapping, and per-port mirror-trigger enable masks.
- System and firmware management registers include `mgir`, `mrsr`, `mlcr`, `mcqi`, `mcc`, `mcda`, `mcam`, `mfgd`, `mgpir`, `mbct`, `mddt`, `mddq`, `mddc`, and `mfde`. They expose hardware/firmware identity, reset commands, LED beaconing, firmware component query/control/data flows, management capability bits, firmware fatal-debug controls/events, peripheral topology, INI/binary transfer to management firmware, downstream-device tunneling/query/control, and firmware debug event payloads.
- PTP/time registers include `mtpps`, `mtutc`, `mtpppc`, `mtpptr`, `mtptpt`, and `mtpcpc`. They configure virtual PPS pins, UTC set/adjust/frequency operations, PTP message types to timestamp or trap, timestamp FIFO records, and correction-field handling.
- Tunnel registers include `tngcr`, `tnumt`, `tnqcr`, `tnqdr`, `tneem`, `tndem`, `tnpc`, `tigcr`, `tieem`, and `tidem`. They configure NVE tunnel type, TTL, flow-label and UDP-source-port hashing, underlay multicast tables, NVE QoS/ECN mapping, tunnel-port learning, IP-in-IP TTL behavior, and IP-in-IP ECN mapping/trap actions.
- Shared-buffer registers include `sbpr`, `sbcm`, `sbpm`, `sbmm`, `sbsr`, and `sbib`. They configure pool size/mode, port-priority or traffic-class quotas, port-pool quota and occupancy, multicast priority quotas, bulk occupancy snapshots, and internal per-port buffers used by features such as egress mirroring.
- `mlxsw_reg_infos[]` registers all known `struct mlxsw_reg_info` descriptors, including many definitions from earlier chunks and all definitions in this chunk. `mlxsw_reg_id_str()` linearly maps a register ID back to a human-readable register name. The final PUDE layout defines fields used to decode port up/down events.

## Control Flow

The dominant control-flow pattern is payload construction:

1. A caller allocates or receives a `char *payload` of the register's declared length.
2. The relevant `mlxsw_reg_*_pack()` helper calls `MLXSW_REG_ZERO()` for full-payload initialization.
3. The helper writes index, operation, and common RW fields through generated setters.
4. Optional follow-up helpers or direct generated setters fill variable bit arrays, repeated records, buffers, or protocol-specific fields.
5. The payload is submitted to the mlxsw register transport for query or write, and any returned payload is decoded through generated getters or explicit unpack helpers.

Router multicast programming follows this pattern closely. `mlxsw_reg_rmft2_common_pack()` zeros the register, writes valid/op/offset/VRF/ingress-RIF key fields, and optionally copies the flexible action set. IPv4 and IPv6 wrappers then set the address-family type and copy DIP/SIP values plus masks. Deletion is represented by packing `v = false` with the same key/offset semantics.

Monitoring and management helpers are thin but encode important sequencing assumptions. Firmware component update uses `mcqi` to query component limits and access granularity, `mcc` to lock/update/verify/activate/cancel the component FSM and retrieve an update handle/error/control state, and `mcda` to transfer data words under that handle. INI/binary transfer to line-card management firmware uses `mbct`: the caller packs an opcode, optionally enables opcode events, attaches up to 1 KB of data through `mlxsw_reg_mbct_dt_pack()`, marks the last chunk, and later unpacks status/FSM state.

Downstream-device access is a nested-register flow. `mlxsw_reg_mddt_pack()` receives an inner `struct mlxsw_reg_info`, bounds the inner register plus a four-byte PRM header against `MLXSW_REG_MDDT_LEN`, fills MDDT slot/device/method/register-id/read-size/write-size fields, and returns `inner_payload` pointing into the embedded register area. The caller then packs the downstream register into that inner region. `mddq` has three separate query flows for slot info, device info, and slot name, all funneled through `__mlxsw_reg_mddq_pack()`.

PTP timestamping is another multi-register flow. `mtpppc` selects message types to timestamp, `mtptpt` maps message types to trap IDs, `mtpcpc` enables traps and correction-field updates globally or per port, and `mtpptr` reads records from per-port ingress/egress timestamp FIFOs. `mlxsw_reg_mtpptr_unpack()` reconstructs the 64-bit timestamp from high/low fields and returns the PTP message type, domain, and sequence ID used to match trapped packets.

Tunnel setup is staged. `tngcr` establishes NVE tunnel type and global VTEP behavior; callers then set underlay VRF/RIF/source addresses and group sizes as needed. `tnumt` populates underlay multicast/flood lists, `tnqcr`/`tnqdr` define DSCP policy, `tneem` and `tndem` define ECN encapsulation/decapsulation matrices, and `tnpc` controls tunnel-port learning on Spectrum-2 style devices. IP-in-IP has a smaller parallel set: `tigcr` for TTL copy/default, `tieem` for encapsulation ECN, and `tidem` for decapsulation ECN and optional traps.

Shared-buffer control is split between configuration and observation. `sbpr`, `sbcm`, `sbpm`, `sbmm`, and `sbib` pack one selected pool/port/class/priority object per payload. `sbpm_unpack()` reads one port-pool occupancy pair. `sbsr` is a bulk read mechanism: callers set ingress/egress port masks and priority/tclass masks after `mlxsw_reg_sbsr_pack()`, then iterate `mlxsw_reg_sbsr_rec_unpack()` records. The comment explicitly warns that too many requested records can exceed the transport MTU and be silently truncated.

## State and Persistence Behavior

This header owns no runtime state beyond compile-time constants and generated inline functions. Persistent state lives in hardware or firmware registers after successful register writes, and in higher-level driver objects that decide when to replay those writes after reload, reset, line-card provisioning, or feature toggles.

Several hardware-persistent domains are represented:

- Router state: ECMP hash seeds and fields, multicast forwarding entries, RIF group membership, egress VID mappings, and multicast action sets persist in switch/router tables until changed or invalidated.
- Environmental state: fan PWM frequency/duty cycle, tachometer thresholds, temperature event thresholds, max-temperature enable/reset behavior, sensor warning state, and fan-under-limit status are firmware/hardware managed and queried by health and hwmon paths.
- Module and peripheral state: EEPROM reads are transient, but module low-power/presence notifications, slot/device topology, INI provisioning state, downstream-device enable/reset state, and binary-transfer FSM state persist in management firmware.
- Firmware update state: MCQI/MCC/MCDA and MBCT flows use update handles, FSM states, status codes, and transfer offsets. The header encodes the fields, while callers must serialize operations and honor alignment, component size, max-write-size, and status transitions.
- Monitoring/mirroring state: analyzer table entries, per-port analyzer enables, sampling rates, parser depth, mirror trigger mappings, mirror trigger enable masks, PTP timestamp/trap configuration, and general-purpose counters remain active until reconfigured.
- Tunnel state: NVE/IP-in-IP global settings, underlay multicast table records, QoS and ECN mappings, tunnel-port learning flags, source addresses, and TTL behavior define packet-processing behavior in hardware.
- Shared-buffer state: pool sizes/modes, class/port/priority quotas, dynamic alpha values, infinite flags, occupancy max tracking, and clear bits are maintained in switch buffer hardware.

The pack helpers mostly zero entire payloads, which is a deliberate safety pattern for reserved fields. Helpers that only set a subset of a register rely on callers to fill additional fields before write, or on hardware defaults/ignored fields. Unpack helpers often tolerate optional output pointers, but not consistently: some helpers check pointers before assignment, while others such as `mlxsw_reg_mgir_unpack()`, `mlxsw_reg_mcqi_unpack()`, `mlxsw_reg_mtpptr_unpack()`, and several `mddq` unpack helpers assume non-NULL outputs.

## Dependencies and Integration Points

The chunk depends on the core mlxsw register-description macros defined earlier in the same header or adjacent headers: `MLXSW_REG_DEFINE`, `MLXSW_REG_ZERO`, `MLXSW_REG`, `MLXSW_ITEM32`, `MLXSW_ITEM32_INDEXED`, `MLXSW_ITEM64`, `MLXSW_ITEM_BUF`, `MLXSW_ITEM_BIT_ARRAY`, and `MLXSW_ITEM32_LP`. These macros generate the typed setters/getters/memcpy helpers used throughout the inline functions.

Kernel dependencies visible in this span include fixed-width integer types, `bool`, `BIT()`, `GENMASK()`, `BITS_PER_BYTE`, `ARRAY_SIZE()`, `WARN_ON()` / `WARN_ON_ONCE()`, and `struct in6_addr`. The code also references mlxsw-specific enums or register concepts defined elsewhere, such as `enum mlxsw_reg_flow_counter_set_type`, `enum mlxsw_reg_tunnel_port`, `struct mlxsw_reg_info`, and `MLXSW_REG_FLEX_ACTION_SET_LEN`.

Major integration points by driver area:

- Router and Spectrum L3 code uses `rigr2`, `recr2`, `rmft2`, and `reiv` to build ECMP, multicast routing, and egress VLAN behavior.
- Hwmon and thermal drivers use fan/temperature registers for PWM, RPM, tach thresholds, sensor names, temperature readings, and warning/fault event decoding.
- Ethtool/module code uses MCIA and MCION to implement EEPROM reads, module page/bank selection, SFP/QSFP/CMIS handling, and module status reporting.
- Devlink, firmware flashing, and line-card management use MGIR, MRSR, MCQI/MCC/MCDA, MCAM, MGPIR, MBCT, MDDT/MDDQ/MDDC, MFGD, and MFDE.
- Mirroring, sampling, ACL/actions, and telemetry code use MPAT/MPAR/MPAGR/MOMTE/MPSC/MGPC/MPRS/MOGCR.
- PTP support uses MTPPS, MTUTC, MTPPPC, MTPPTR, MTPTPT, and MTPCPC alongside trap handling and timestamp FIFO reads.
- VXLAN/NVE/IP-in-IP offload code uses TNGCR/TNUMT/TNQCR/TNQDR/TNEEM/TNDEM/TNPC/TIGCR/TIEEM/TIDEM.
- Devlink shared-buffer and QoS code uses SBPR/SBCM/SBPM/SBMM/SBSR/SBIB for pool, threshold, and occupancy configuration/reporting.
- Core register transport and diagnostics use `mlxsw_reg_infos[]` and `mlxsw_reg_id_str()` to validate/register supported IDs and print readable names in errors/logs.

## Risks and Edge Cases

- These definitions are layout-critical. A wrong offset, width, index stride, record count, or length constant silently corrupts firmware commands because generated accessors will write the wrong payload bits.
- Several helpers set only a safe baseline. For example, `mlxsw_reg_recr2_pack()` sets seed and symmetric hash but does not enable hash fields; `mlxsw_reg_tngcr_pack()` sets default TTL/hash/group behavior but not underlay VRF/RIF/source addresses; `mlxsw_reg_sbsr_pack()` only sets `clr`, leaving masks to callers. Tests must verify full caller-side payload completion.
- Access qualifiers matter. Some fields are `Index`, `OP`, `WO`, or `RO`, but the C accessors do not enforce register-operation legality. Callers can accidentally set read-only fields or omit required index fields unless reviewed against the hardware spec.
- `mlxsw_reg_mddt_pack()` truncates the nested transfer length after `WARN_ON()` if the embedded register would exceed the MDDT payload. That prevents overflow, but a caller that ignores the warning could send a partial downstream register.
- `mlxsw_reg_mbct_dt_pack()` returns early on `data_size > 1024`, leaving an already-packed MBCT opcode payload without updated data fields. Callers must treat the warning as a hard failure.
- `mlxsw_reg_mcda_pack()` copies `size / 4` words by casting `&data[i * 4]` to `u32 *`. Callers must honor MCQI word-size and DWORD-alignment constraints; unaligned or non-DWORD trailing data is not copied by this helper.
- Temperature conversion is subtle for negative signed 16-bit firmware values. `MLXSW_REG_MTMP_TEMP_TO_MC()` relies on sign handling and two's-complement reconstruction; regressions here affect hwmon readings and threshold comparisons.
- `mtbr` declares `REC_MAX_COUNT` as 1 in this source, despite register comments allowing a range up to 255 records. Callers expecting bulk reads of many sensors must use the actual declared mlxsw payload length or update the length/record constants consistently.
- `sbsr` can return truncated responses when masks request too many records. Because the hardware gives no special truncation notice, callers must bound mask breadth and record iteration against the requested response size.
- Many unpack helpers assume non-NULL output pointers. Passing optional NULLs inconsistently can crash in inline code, especially in firmware/device query paths.
- Register support varies by ASIC generation. Comments mark fields or whole registers as reserved on Spectrum, Spectrum-1, Spectrum-2, SwitchX, IB switches, or Quantum. Higher layers must gate writes with capability bits such as MCAM or device-family checks.
- The `mlxsw_reg_infos[]` table must stay synchronized with new register definitions. A missing entry can break generic lookup/validation or reduce diagnostic quality even if the accessor macros compile.
- ECN and trap mappings are matrix-like. NVE/IP-in-IP encapsulation and decapsulation mappings must cover all relevant overlay/underlay ECN combinations, and trap IDs must match the trap subsystem definitions.
- Shared-buffer dynamic threshold values use encoded alpha values with a documented range of 1..14 plus infinity forms. Treating these fields as raw cells when the pool is dynamic will misconfigure congestion behavior.

## Test Signals

Useful validation signals for this chunk include:

- Compile coverage of all generated accessors and inline helpers under mlxsw configurations that include Spectrum routing, hwmon, devlink flash, line cards, PTP, tunneling, mirroring, and shared-buffer support.
- Register payload unit tests or debug assertions that pack representative payloads and compare byte-level layouts for `rmft2`, `mcia`, `mcqi/mcc/mcda`, `mddt/mddq`, `tngcr/tnumt`, `tndem/tidem`, and shared-buffer registers against hardware-spec fixtures.
- ECMP and multicast routing tests that verify RECR2 hash-field enable masks, RIGR2 next-group chaining, RMFT2 IPv4/IPv6 address/mask/action programming, and REIV egress VID mapping.
- Hwmon/thermal tests that cover positive and negative MTMP readings, max-temperature reset/enable, sensor names, MTWE warning bits, MTBR error-status values, fan PWM duty cycle, tachometer limits, and FORE fault extraction.
- Module EEPROM tests for SFP, QSFP, QSFP-DD, OSFP, CMIS flat memory, high/low I2C addresses, page/bank selection, 48-byte versus 128-byte MCIA capability, no-module/no-EEPROM/I2C-error statuses, and MCION presence/low-power bits.
- Firmware flashing tests that exercise MCQI capability discovery, MCC lock/update/verify/activate/cancel transitions, MCDA alignment and max write sizes, update-handle propagation, MBCT erase/data/activate/status flows, and error-state cleanup.
- Line-card/downstream-device tests for MGPIR topology discovery, MDDQ slot/device/name multi-message sequencing, MDDC reset/device-enable behavior, and MDDT nested register tunneling with oversized-register warning coverage.
- Mirroring/sampling tests for local and remote SPAN, RSPAN VLAN/L2/L3 encapsulation, IPv4/IPv6 mirror tunnel fields, per-port MPAR enables, MPAGR trigger mapping, MOMTE trigger masks, MPSC sampling rate bounds, and MGPC clear/read behavior.
- PTP tests for UTC set/immediate adjust/frequency adjust bounds, virtual PPS programming, ingress/egress timestamp message masks, trap IDs, timestamp FIFO clear and record count handling, and correction-field enablement.
- Tunnel offload tests for NVE type selection, underlay source IPv4/IPv6 programming, UDP source-port hash prefix, flow-label copy/hash modes, multicast/flood TNUMT chains, DSCP defaults, all ECN map combinations, tunnel-port learning, and IP-in-IP TTL/ECN behavior.
- Shared-buffer tests through devlink/SB APIs for static versus dynamic pool modes, infinity flags, alpha range validation, per-port and per-PG quotas, multicast priority quotas, SBSR bulk occupancy masking/truncation bounds, max-occupancy clear semantics, and SBIB egress-mirroring headroom.
- Event and diagnostic tests that decode PUDE port events and MFDE firmware debug events, and that verify `mlxsw_reg_id_str()` returns expected names for every register listed in `mlxsw_reg_infos[]` and `*UNKNOWN*` for unmapped IDs.
