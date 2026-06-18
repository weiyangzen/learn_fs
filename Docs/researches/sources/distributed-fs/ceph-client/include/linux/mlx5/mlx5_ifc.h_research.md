# Research: sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005889`: lines 1-10839, `Docs/researches/chunks/subset-b-005889_research.md`
- `subset-b-005890`: lines 10840-13703, `Docs/researches/chunks/subset-b-005890_research.md`

## Chunk Research

### subset-b-005889: lines 1-10839

# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc.h lines 1-10839

## Scope And Purpose

This chunk covers the first 10,839 lines of the Mellanox/NVIDIA mlx5 firmware interface header. It is an ABI description used by the Linux mlx5 core, Ethernet, RDMA, eswitch, steering, virtualization, and low-level management paths to construct command mailbox buffers, parse command responses, interpret asynchronous events, and access firmware registers.

The file is not algorithmic runtime code. Its primary purpose is to provide exact bit layouts for hardware/firmware contracts. Nearly every definition is an enum, macro, struct, or union where fields are declared as bit-width arrays such as `u8 field[0x10]`. Callers normally use mlx5 bitfield helper macros from the surrounding driver, for example generated-field accessors such as `MLX5_SET`, `MLX5_GET`, and `MLX5_ADDR_OF`, to populate these layouts in command buffers. Any field movement or width change here can silently break hardware command encoding.

The chunk starts with event type codes, HCA capability operation modifiers, general object IDs, and command opcodes. It then defines capability pages, match and flow-steering layouts, queue and memory object contexts, event payload formats, command input/output mailboxes for create/query/modify/destroy operations, allocator/deallocator commands, and the beginning of the port/register access block. The chunk ends inside `struct mlx5_ifc_mtutc_reg_bits`; the rest of the register catalog and later advanced object definitions continue after line 10,839 and are outside this work item.

## Interface Shape

The dominant API pattern is:

- Command opcode enums, especially `MLX5_CMD_OP_*`, identify firmware operations.
- Input structs named `mlx5_ifc_<operation>_in_bits` encode `opcode`, often `uid`, `op_mod`, object identifiers, optional flags/selectors, and an embedded context.
- Output structs named `mlx5_ifc_<operation>_out_bits` encode `status`, `syndrome`, returned identifiers, and optional returned contexts or counters.
- Context structs named `mlx5_ifc_*c_bits` encode persistent device object state such as QPs, CQs, EQs, SQs, RQs, TIRs, TISs, DCTs, SRQs, XRQs, RMPs, RQTs, MKEYs, flow tables, vport contexts, and scheduling elements.
- Capability structs are selected through `union mlx5_ifc_hca_cap_union_bits`, with `QUERY_HCA_CAP` and `SET_HCA_CAP` choosing the page through `op_mod`.
- Variable-length payloads use C flexible arrays, zero-length arrays, or `DECLARE_FLEX_ARRAY`; callers must allocate enough mailbox space for PAS lists, destination lists, counters, register payloads, or variable numbers of vport/GID/PKEY entries.

This header depends on `mlx5_ifc_fpga.h` for FPGA capability fields included in the HCA capability union.

## Command Opcode And Object Taxonomy

The early enum block defines firmware command opcodes. The commands cover:

- HCA lifecycle and negotiation: `QUERY_HCA_CAP`, `QUERY_ADAPTER`, `INIT_HCA`, `TEARDOWN_HCA`, `ENABLE_HCA`, `DISABLE_HCA`, `QUERY_PAGES`, `MANAGE_PAGES`, `QUERY_ISSI`, `SET_ISSI`, and `SET_DRIVER_VERSION`.
- Function and migration management: scalable functions, SF partitioning, suspend/resume VHCA, query/save/load VHCA migration state, delegated VHCA query, eswitch vport create/destroy, and VUID query.
- Memory and page-fault handling: `CREATE_MKEY`, `QUERY_MKEY`, `DESTROY_MKEY`, special contexts, page-fault resume, MEMIC allocation, and UMEM/UCTX commands.
- Events and completion resources: EQ/CQ create/query/modify/destroy and generated EQ events.
- RDMA transports: QP state transitions, PSV, SRQ, XRC SRQ, DCT, XRQ, multicast attach/detach, XRCD, transport domain, PD, UAR, and DCI/DC parameter commands.
- Vport and eswitch management: vport state/context, RoCE addresses, GIDs/PKEYs, VNIC environment counters, vport counters, QoS scheduling, monitor counters, and L2 table entries.
- Packet steering: TIR/TIS/SQ/RQ/RMP/RQT objects, flow tables/groups/entries, flow counters, packet reformat contexts, modify-header contexts, match definers, general objects, and software steering synchronization.
- Offloads and crypto synchronization: IPsec/MACsec/PSP capability fields, crypto sync, PSP key commands, and general object access for newer object types.
- Management register access: `ACCESS_REG`, MAD IFC, WOL/ROL, link/port and PCIe register layouts beginning near the end of this chunk.

Object type enums identify both general objects and legacy object IDs. General object examples include SW ICM, GENEVE TLV options, virtio queues, match definers, STC/RTC/STE, modify-header patterns, page tracking, and header modify arguments. Legacy object IDs cover MKEY, QP, PSV, RMP, SRQ/XRC SRQ, RQ, SQ, TIR, TIS, DCT, XRQ, RQT, flow counters, CQ, and flow-table aliases. Capability bitmasks such as `MLX5_GENERAL_OBJ_TYPES_CAP_*` advertise which general object classes are supported.

## Capability Layouts

`struct mlx5_ifc_cmd_hca_cap_bits` is the central general HCA capability page. It exposes object limits, feature bits, port configuration, queue capabilities, memory registration features, event support, virtualization support, flow counter limits, steering formats, timestamp formats, dynamic MSI-X support, scalable functions, migration support, crypto/IPsec/TLS support, and many resource log-size maxima. Driver code uses this page before enabling optional paths, so these bit positions are high-risk compatibility points.

`struct mlx5_ifc_cmd_hca_cap_2_bits` extends the general capability model with migration, multi-plane, cross-VHCA access, newer object-type bits, software VHCA IDs, fixed-buffer MKEY entity sizes, generate-WQE support, max EQs, load balancing, delegated VHCA management, and other newer features.

Specialized capability pages include:

- `mlx5_ifc_flow_table_nic_cap_bits`, `mlx5_ifc_flow_table_eswitch_cap_bits`, `mlx5_ifc_flow_table_prop_layout_bits`, `mlx5_ifc_flow_table_fields_supported_bits`, and `_supported_2_bits` for NIC RX/TX, RDMA, sniffer, FDB, ACL, flow counters, packet reformat, VLAN, decap, modify-header, IPsec/MACsec/PSP, ASO, reparse, and SW/HW steering properties.
- `mlx5_ifc_wqe_based_flow_table_cap_bits` for WQE-driven steering objects such as STE/STC/RTC, allocation granularity, RTC modes, supported STE formats, STC action types, and header insert/remove types.
- `mlx5_ifc_e_switch_cap_bits` and `mlx5_ifc_esw_cap_bits` for eswitch manager features, VLAN strip/insert, shared ACLs, root flow tables on another eswitch, encapsulation/decapsulation, scalable function base IDs, and merged eswitch support.
- `mlx5_ifc_qos_cap_bits` for packet pacing, eswitch/NIC scheduling, bandwidth share, rate limits, TSAR element types, meter ASO allocation, and queue-group limits.
- `mlx5_ifc_per_protocol_networking_offload_caps_bits` for checksum, VLAN, LRO/LSO, RSS, inline mode, tunnel stateless offloads, SW parser, Geneve, VXLAN-GPE, MPLS, and trailer insertion.
- `mlx5_ifc_roce_cap_bits`, `mlx5_ifc_atomic_caps_bits`, and `mlx5_ifc_odp_cap_bits` for RoCE versions/ports, atomic operation and size support, and ODP page-fault schemes.
- `mlx5_ifc_tls_cap_bits`, `mlx5_ifc_ipsec_cap_bits`, `mlx5_ifc_macsec_cap_bits`, `mlx5_ifc_psp_cap_bits`, and `mlx5_ifc_crypto_cap_bits` for crypto/offload algorithms, object counts, replay-window limits, DEK/KEK support, and synchronization requirements.
- `mlx5_ifc_device_mem_cap_bits` for MEMIC and software ICM address ranges used by software steering, header modify, indirect encap, and device memory operations.
- `mlx5_ifc_virtio_emulation_cap_bits` and `mlx5_ifc_tlp_dev_emu_capabilities_bits` for virtio and PCIe/TLP emulation support.
- `mlx5_ifc_debug_cap_bits` and `mlx5_ifc_device_event_cap_bits` for core dumps, resource dumps, stall detection, and user event masks.

`union mlx5_ifc_hca_cap_union_bits` is the selector container used by HCA-cap query/set commands. The union size reserves an 0x8000-bit page, so callers must not treat the specific member size as the full mailbox payload size unless they are explicitly building a minimal buffer for a known command path.

## Flow Steering And Match Structures

The flow steering schema is one of the largest parts of this chunk.

`mlx5_ifc_fte_match_set_lyr_2_4_bits` encodes Ethernet, VLAN, IP, TCP/UDP, protocol, TTL/hop-limit, L4 type, IPv4/IPv6 source and destination fields. `union mlx5_ifc_ipv6_layout_ipv4_layout_auto_bits` overlays IPv6 and IPv4 forms so the same match structure can support either address family.

`mlx5_ifc_fte_match_set_misc_bits` through `misc5_bits` extend matching with GRE/NVGRE keys, VXLAN/Geneve VNIs, Geneve TLV existence/data, BTH opcode and destination QP, IP flow labels, MPLS, metadata registers `reg_c_0` through `reg_c_7`, metadata register A, security syndromes, GTP-U fields, ICMP/ICMPv6 fields, programmable sample fields, MACsec tags, and tunnel header words. `mlx5_ifc_fte_match_param_bits` aggregates outer headers, inner headers, and all misc groups into the full match payload.

Flow destinations are represented by `mlx5_ifc_dest_format_struct_bits`, `mlx5_ifc_extended_dest_format_bits`, and `union mlx5_ifc_dest_format_flow_counter_list_auto_bits`. Destination types include vport, flow table, TIR, VHCA RX, sampler, uplink, and table-type destinations. Extended destinations can bind a packet reformat ID and destination owner VHCA ID.

`mlx5_ifc_flow_context_bits` is the complete flow table entry context. It combines VLAN push contexts, group/flow tags, action bitmask, flow source, encrypt/decrypt object type and ID, destination list size, flow counter list size, packet reformat ID, modify-header ID, full match value, up to four execute-ASO controls, and a flexible destination/counter list. Action bits include allow, drop, forward, count, packet reformat, decap, modify header, VLAN pop/push, crypto encrypt/decrypt, and ASO execution.

The create/query/modify/delete flow commands are:

- `create_flow_table`, `query_flow_table`, `modify_flow_table` is outside this chunk, and `destroy_flow_table`, using `mlx5_ifc_flow_table_context_bits`.
- `create_flow_group`, `query_flow_group`, and `destroy_flow_group`, using match criteria, group ID, start/end flow indexes, group type, and optional match definer ID.
- `set_fte`, `query_fte`, and `delete_fte`, using table type, table ID, flow index, modify masks, and `flow_context`.
- `alloc_flow_counter`, `query_flow_counter`, and `dealloc_flow_counter`, with bulk flow-counter support macros and counter arrays.

Match definer support appears in `mlx5_ifc_match_definer_format_*_bits`, `mlx5_ifc_match_definer_match_mask_bits`, and `mlx5_ifc_match_definer_bits`. These structures define compressed programmable match formats and selectors for SW/HW steering flows. They are linked to general object create/query headers and match-definer object commands. The selector constants and fixed selector counts (`MLX5_IFC_DEFINER_DW_SELECTORS_NUM`, `MLX5_IFC_DEFINER_BYTE_SELECTORS_NUM`) are integration points for steering code that packs hardware match templates.

Packet reformat support includes `mlx5_ifc_packet_reformat_context_in_bits`, create/query/dealloc commands, anchor constants, and `enum mlx5_reformat_ctx_type`. Reformat types cover L2-to-tunnel, tunnel-to-L2, ESP tunnel/transport add/remove, PSP add/remove, generic insert/remove header, and MACsec add/remove.

Modify-header support includes `mlx5_ifc_set_action_in_bits`, `mlx5_ifc_add_action_in_bits`, `mlx5_ifc_copy_action_in_bits`, the set/add/copy action union, action type constants, and action field IDs for outer headers, IPv4/IPv6 fields, L4 ports, metadata registers, TCP sequence/ack numbers, IPsec/PSP syndrome, and enhanced metadata. `alloc_modify_header_context` creates an ID later referenced from `flow_context.modify_header_id`.

## Queue, Transport, And Memory Object Contexts

The transport object contexts define the persistent state programmed into hardware.

`mlx5_ifc_qpc_bits` is the QP context. It contains QP state, service type, path migration state, protection domain, MTU, send/receive queue sizes and strides, UAR page, user index, remote QPN, primary/secondary address paths, retry/RNR fields, PSNs, CQs, XRC domain, doorbell record address, Q key, SRQ/RMP/XRQ binding, hardware/software counters, DC access key, atomic modes, checksum modes, timestamp format, DCI stream parameters, and ordering flags. QP lifecycle commands include create, query, destroy, and state transitions: reset-to-init, init-to-init, init-to-RTR, RTR-to-RTS, RTS-to-RTS, SQERR-to-RTS, SQD-to-RTS, to-error, and to-reset. Several transition outputs return ECE data.

`mlx5_ifc_ads_bits` is an address path descriptor used inside QP and DCT contexts. It carries P_Key index, plane index, GRH/LID fields, timeout, source address index, static rate, hop limit, traffic class, flow label, remote GID/RIP, DSCP/ECN/UDP source port, VLAN priority/SL, VHCA port, and remote MAC.

`mlx5_ifc_wq_bits` is a common work queue layout embedded by SQ, RQ, RMP, and XRQ-style contexts. It holds WQ type, signature, padding, page offset, low-water mark, PD, UAR page, doorbell record address, hardware/software counters, log stride/page/size, UMEM IDs and offsets, hairpin fields, striding RQ parameters, SHAMPO fields, and a flexible PAS list. This is a key variable-length allocation point: PAS count must match queue size/page geometry.

Send/receive object contexts include:

- `mlx5_ifc_sqc_bits` for SQ state, UMR/SWP support, hairpin peers, CQN, packet pacing, TIS list size, QoS queue group, first TIS, and embedded WQ.
- `mlx5_ifc_rqc_bits` for RQ state, delay drop, scatter FCS, memory RQ type, CQN, counter set, RMP binding, hairpin peer, SHAMPO reservation controls, and embedded WQ.
- `mlx5_ifc_rmpc_bits` for receive memory pool state and embedded WQ.
- `mlx5_ifc_rqtc_bits` for receive queue table contents, including flexible arrays of RQ numbers or RQ/VHCA pairs.
- `mlx5_ifc_tirc_bits` for TIR dispatch type, TLS enable, LRO merge controls, inline RQN, tunneled offload, RSS indirection table, hash function, self-loopback block, transport domain, Toeplitz key, and outer/inner hash field selectors.
- `mlx5_ifc_tisc_bits` for TIS TX path attributes, TLS, LAG affinity, priority, transport domain, underlay QPN, and PD.

Shared receive and advanced receive contexts include `mlx5_ifc_srqc_bits`, `mlx5_ifc_xrc_srqc_bits`, and `mlx5_ifc_xrqc_bits`. XRQ adds tag-matching topology and rendezvous offload fields. Commands cover create/query/destroy/arm for SRQ, XRC SRQ, and XRQ. `arm_rq`, `arm_xrc_srq`, and `arm_xrq` program low-water marks that drive limit events.

`mlx5_ifc_dctc_bits` defines DCT state, user index, CQN, counters, atomic and ordering modes, SRQ/XRQ binding, PD, class/flow-label fields, DC access key, MTU, port, P_Key, address index, hop limit, violation count, DSCP/ECN, and ECE. DCT commands include create, query, destroy, drain, and arm-for-key-violation.

`mlx5_ifc_cqc_bits` and `mlx5_ifc_eqc_bits` define completion and event queues. CQ context fields cover status, CQE size, compression, overrun ignore, arm state, page offset, log size, UAR, moderation period/count, event queue number or APU element, page size, notification indexes, producer/consumer counters, and doorbell record address. EQ context fields cover status, completion/event mode, arm/fire state, page size, interrupt vector, producer/consumer counters, and PAS list. Commands create/query/modify/destroy CQs and EQs; `gen_eqe` injects an EQE payload.

`mlx5_ifc_mkc_bits` defines MKEY state. It includes access mode, access permissions, relaxed ordering, UMR enable, QPN binding, PD, start address, length, BSF size, crossing VHCA target, translation size, page size, TPH steering, and other memory-key attributes. MKEY commands create, query, and destroy memory keys with variable KLM/PAS/MTT translation lists.

Other allocator-style resources include PD, UAR, transport domain, XRCD, PSV, q-counter, flow counter, packet reformat context, modify-header context, and scheduling elements. The pattern is consistently create/alloc returns an ID, query reads a context when supported, modify applies a mask/context, and destroy/dealloc consumes the ID.

## Vports, Eswitch, QoS, And Virtualization

Vport state and context layouts support both NIC vports and eswitch vports.

`mlx5_ifc_nic_vport_context_bits` contains inline mode, local loopback suppression, RoCE enable, change-event arms, affiliation criteria/VHCA ID, MTU, system image GUID, port GUID, node GUID, qkey violation counter, promiscuous mode flags, allowed-list type/size, permanent MAC, and flexible current UC MAC list.

`mlx5_ifc_hca_vport_context_bits` covers InfiniBand/HCA vport properties: field select, SM/raw capabilities, GRH requirements, port plane count, physical/admin state, GUIDs, capability masks, LID/SM LID, subnet timeout, SL, and PKEY/QKEY violation counters.

`mlx5_ifc_esw_vport_context_bits` covers eswitch-specific VLAN strip/insert settings, FDB-to-vport register-C behavior, VLAN IDs/PCP/CFI, and SW steering vport ICM addresses for RX/TX. Field-select structs restrict which parts can be modified.

The command set includes query/modify NIC vport context, query/modify HCA vport context, query/modify eswitch vport context, create/destroy eswitch vport, query/modify vport state, query vport counters, query VNIC diagnostic environment, query VUID, query delegated VHCA, and create/destroy QoS scheduling elements.

QoS scheduling is represented by `mlx5_ifc_scheduling_context_bits`, `mlx5_ifc_tsar_element_bits`, `mlx5_ifc_vport_element_bits`, `mlx5_ifc_vport_tc_element_bits`, and `union mlx5_ifc_element_attributes_bits`. Scheduling commands identify hierarchy (`E_SWITCH` or `NIC`), element ID, element type, parent element, bandwidth share, max average bandwidth, and max bandwidth object ID. Modify masks include bandwidth share and max average bandwidth.

Scalable function and migration definitions are mostly advertised in capability fields in this chunk. The actual SF and VHCA migration command structs begin after line 10,839, so this chunk only establishes the opcodes and capability bits for those later command layouts.

## Events, Counters, Health, And Diagnostics

Event type constants define completion events, path migration, communication established, send queue drained, last WQE, SRQ limit, DCT close/key violation, CQ error, WQ/SRQ catastrophic errors, page faults, internal error, port state change, GPIO, RCP event, doorbell/BlueFlame congestion, stall VL, dropped packet logged, command interface completion, page request, FPGA error, and FPGA QP error.

`union mlx5_ifc_event_auto_bits` overlays event payloads for completion, DCT, QP, WQE-associated page faults, RDMA page faults, CQ errors, dropped packet logs, port state changes, GPIO, DB/BF congestion, stall VL, and command completion. Event-specific structs expose key identifiers such as CQN, QPN/RQN/SQN, DCT number, page-fault token data, fault address/length, syndrome, and port/VL information.

Counters are defined at several levels:

- Physical-layer and Ethernet register counter groups: `phys_layer_*`, `ib_port_cntrs`, `ib_ext_port_cntrs`, `eth_*_cntrs_grp_data_layout_bits`, `pcie_perf_cntrs`, and unions for PPCNT/MPCNT register payloads.
- Vport counters: `query_vport_counter_out_bits` uses repeated `mlx5_ifc_traffic_counter_bits` for IB/Ethernet unicast, multicast, broadcast, errors, and loopback.
- Q counters: `query_q_counter_out_bits` exposes RDMA request counts and many error counters, including out-of-buffer, out-of-sequence, duplicate requests, retry errors, protection errors, remote access/operation errors, CQ overflow, flush errors, and RoCE adaptive retransmission counters.
- Flow counters: `mlx5_ifc_traffic_counter_bits` arrays returned from `query_flow_counter`.
- Monitor counters: fixed monitor-counter setup supports PPCNT error counters and Q-counter out-of-buffer monitoring.
- VNIC diagnostic statistics: `mlx5_ifc_vnic_diagnostic_statistics_bits` tracks error queues, steering discards, vport-down drops, EQ overruns, invalid/quota-exceeded commands, internal RQ OOB, CQ overrun, packet steering failures, BAR/UAR access, and ODP page faults.

`mlx5_ifc_health_buffer_bits` maps firmware health dump fields such as assertion pointers, time, firmware version, hardware ID, severity, syndrome, and extended syndrome. Resource dump layouts define menu records, command/info/error/resource/terminate segments, and the combined menu response. These are used by debug and devlink-style diagnostics.

## Register Access Layouts In This Chunk

`mlx5_ifc_access_register_in_bits` and `_out_bits` are the generic register mailbox formats. They select read/write through op_mod, carry a register ID, an argument, and a flexible register data payload. The register-specific structs near the end of this chunk describe the payloads passed through this mechanism.

Port and link register layouts covered before line 10,839 include:

- `sltp` and `slrg` for lane tuning/status and grading.
- `pvlc`, `pude`, `ptys`, `mlcr`, `ptas`, `pspa`, `pqdr`, `ppsc`, `pplr`, and `pplm` for port VLs, admin/oper status, protocol/link speed advertisement and operation, beacon controls, tuning algorithm settings, port/subport addressing, priority drop, pause/stall controls, local loopback, port profile, retransmission, and FEC override controls.
- `ppcnt` for port counters, with counter-group union selection.
- `mpein` and `mpcnt` for PCIe interface information and PCIe counters.
- `ppad`, `pmtu`, `pmpr`, `pmpe`, `pmpc`, `pmlpn`, `pmlp`, `pmaos`, `plpc`, `plib`, `plbf`, `pipg`, `pifr`, `pfcc`, `pelc`, `peir`, `mpegc`, and `mpir` for MAC address, MTU, module attenuation/status, module mapping, module admin state, link profile capability, IB port mapping, local loopback force, IPG, port filtering, priority flow control, enhanced link controls, error injection/reporting, PCIe congestion, and multi-host/port inventory.
- `mtutc` begins at the end of the chunk and defines UTC time/frequency-adjustment operations; its full struct continues after this chunk.

Because register access uses a generic command wrapper, the register structs are integration points for management code rather than standalone commands. Callers must match register IDs, op_mod read/write direction, local port/module/lane selectors, and group selectors to the correct register payload.

## Control Flow And State Transitions

There is no executable control flow in this header, but it encodes hardware control flow through state fields and command sequences:

- HCA lifecycle usually follows capability/ISSI negotiation, page query/manage, enable/init, normal object creation, teardown/disable, and page return. `manage_pages` and `query_pages` model firmware page ownership and must agree with the driver's DMA page allocator.
- QPs progress through `RST`, `INIT`, `RTR`, `RTS`, `SQER`, `SQD`, `ERR`, and suspended states using distinct transition commands. Transition inputs include optional parameter masks and full/partial QP context fields.
- SQ, RQ, RMP, SRQ, XRQ, DCT, CQ, and EQ objects have state fields and arm/modify operations. Driver code must set only supported modify masks and use valid state transitions.
- Flow steering progresses from create flow table, create group, set FTE, attach destinations/reformat/modify-header/counter IDs, then query/delete/destroy. Flow-table miss actions and root selection are represented by table contexts and command fields.
- MKEY lifecycle is create/query/destroy with variable translation backing. UMR-enabled or crossing VHCA MKEYs depend on capability bits and access-mode encoding.
- Vport and eswitch operations use field-select masks to modify only chosen attributes; changing context fields without setting the corresponding field-select bit will usually be ignored by firmware.
- Register control uses `ACCESS_REG` read or write operations. State persistence depends on the specific register semantics, not on this header.

The `status` and `syndrome` fields in nearly every output struct are the firmware error boundary. Callers must check status before consuming returned IDs or contexts.

## State And Persistence Behavior

The structures describe several classes of persistent state:

- Device-global state: HCA capabilities, enabled/initialized state, firmware pages, ISSI, driver version, device memory/SW ICM ranges, and register settings.
- Per-function or per-vport state: NIC/HCA/eswitch vport contexts, RoCE address table entries, GID/PKEY tables, L2 table entries, VUIDs, delegated VHCA data, scalable-function capabilities, and vport counters.
- Hardware object state: QP, CQ, EQ, MKEY, SQ, RQ, RMP, TIR, TIS, RQT, SRQ, XRC SRQ, XRQ, DCT, flow table/group/FTE, flow counter, packet reformat context, modify-header context, match definer, scheduling element, PD, UAR, TD, XRCD, and PSV.
- Runtime event/counter state: event queues, command completion events, page faults, diagnostic counters, monitor counters, health buffer state, and resource dumps.

Flexible PAS arrays and UMEM fields imply persistent DMA mappings or user memory registrations owned by objects. Create/modify commands that include PAS arrays require correct object sizing, page size, page offset, UMEM validity, and doorbell address handling. Destroy/dealloc commands release firmware object IDs but do not by themselves clean up all higher-level driver references; the driver must synchronize teardown with any software objects, queues, NAPI contexts, RDMA resources, or flow rules that used the ID.

Many counters have explicit `clear` bits in query commands or register payloads. A query with clear can mutate device counter state. Test and diagnostic tools must avoid using clear accidentally when they only intend to sample.

## Dependencies And Integration Points

The header is consumed by multiple mlx5 driver subsystems:

- mlx5 core command interface: builds mailbox buffers using opcode/input/output layouts, parses `status` and `syndrome`, and dispatches completion events.
- Ethernet driver: uses NIC offload capabilities, TIR/TIS/RQ/SQ/RQT contexts, RSS fields, LRO/LSO capabilities, packet pacing, counters, vport context, port registers, and flow steering.
- RDMA driver: uses QP, CQ, EQ, SRQ, XRC, DCT, MKEY, PD, UAR, RoCE, ODP, atomic, address path, GID/PKEY, MAD, and page-fault formats.
- Eswitch and representor code: uses eswitch capabilities, FDB/ACL flow table properties, vport contexts, FDB-to-vport metadata, cross-VHCA access, delegated VHCA, and QoS scheduling.
- Devlink/diagnostics: uses health buffer, resource dumps, counters, register access, physical-layer status, module status, link profiles, and PCIe counters.
- Crypto/offload paths: use TLS, IPsec, MACsec, PSP, crypto synchronization, flow encrypt/decrypt action fields, packet reformat types, and security syndrome match/action fields.
- Software/HW steering code: uses match-definer formats, SW ICM capabilities, STE/STC/RTC capability fields, flow-table contexts, modify-header actions, packet reformat contexts, and general object headers.
- Virtualization/emulation paths: use virtio emulation, TLP device emulation, UCTX/UMEM opcodes, scalable function capabilities, VUID, VHCA migration opcodes/capabilities, and cross-VHCA object access.

The ABI also integrates with standard kernel definitions outside this header: `u8` typedefs, `BIT()`, `DECLARE_FLEX_ARRAY`, command mailbox allocation helpers, DMA mapping/page allocation code, network/RDMA object lifecycles, and endian/bitfield accessor macros.

## Risks And Edge Cases

- Bit layout drift is the primary risk. These structs are ABI definitions; normal C struct alignment is intentionally bypassed by bit-width arrays, and callers rely on exact offsets. A field rename may be harmless to firmware but can break callers using generated accessor names.
- Variable-length command buffers are easy to size incorrectly. PAS lists, flow destinations, counter arrays, register payloads, current MAC lists, GID/PKEY arrays, and flexible queue/table entries require command-specific size calculations.
- Capability gating is mandatory. Many command layouts exist even when firmware does not support the feature. Callers must test the relevant capability bit before issuing commands or setting fields such as crypto, PSP, MACsec, match definers, SW steering, SHAMPO, migration, cross-VHCA, SF, dynamic MSI-X, ODP, atomics, and WQE-based flow tables.
- Field-select and modify masks are subtle. Modify commands often carry a full context but only selected fields should be honored. Missing or overbroad masks can produce partial updates, ignored writes, or firmware errors.
- State machine misuse can corrupt runtime behavior. QP/SQ/RQ/CQ/EQ/DCT/SRQ transitions must match firmware state rules; using create contexts as modify contexts without respecting state and masks is risky.
- Object IDs are reused across domains. Fields named `qpn`, `sqn`, `rqn`, `cqn`, `dctn`, `tirn`, `tisn`, `rqtn`, and `mkey_index` have domain-specific width and ownership. Passing an ID from the wrong namespace may compile but fail in firmware.
- Counter reads may be destructive when `clear` is set. Diagnostics and tests need to distinguish sampling from clear-on-read behavior.
- Cross-VHCA and alias-object access carries security and isolation risk. Access keys, owner VHCA IDs, software/hardware VHCA ID types, and object type permissions must be checked carefully.
- Register write paths can affect physical link state, module state, FEC, pause/PFC, loopback, PCIe behavior, and port profiles. Generic `ACCESS_REG` code must validate register ID, local port/module/lane selectors, and permissions.
- Reserved fields should stay zero unless a local driver path explicitly documents otherwise. Nonzero reserved bits can cause firmware rejection or undefined behavior across device generations.
- The chunk boundary cuts through `mtutc`; any final per-file research must merge later chunks before describing the complete time register and subsequent register/object definitions.

## Test Signals

Because this header encodes an ABI, the strongest test signals are compile-time layout usage and hardware/firmware command execution rather than unit tests of this file itself:

- Build coverage from mlx5 core, mlx5e, mlx5_ib, eswitch, devlink, steering, and crypto/offload code catches missing names, renamed fields, or syntax problems.
- Command selftests or integration tests should issue representative create/query/modify/destroy flows for QP, CQ, EQ, SQ, RQ, TIR, TIS, RQT, MKEY, flow table/group/FTE, flow counters, packet reformat, modify-header, vport context, and register access.
- Capability query tests should verify that `QUERY_HCA_CAP` pages decode correctly for general, general2, Ethernet offload, ODP, atomic, RoCE, flow table, eswitch, QoS, debug, crypto, TLS, IPsec, MACsec, PSP, device memory, and virtio/TLP emulation pages on supported devices.
- Negative command tests should validate firmware `status`/`syndrome` handling for unsupported capability fields, invalid op_mod values, invalid state transitions, malformed PAS lengths, wrong object IDs, and overbroad modify masks.
- Flow steering tests should exercise outer/inner match fields, misc match sets, metadata registers, Geneve/VXLAN/GTP-U/MPLS/IPsec/MACsec/PSP fields, action bit combinations, destination lists, counters, packet reformat IDs, modify-header IDs, match definers, and delete/destroy cleanup.
- RDMA and Ethernet runtime tests should validate QP transitions, CQ moderation/compression, EQ event delivery, RQ/SQ hairpin and striding modes, RQT/RSS behavior, RoCE address/GID/PKEY programming, ODP page-fault resume, and MKEY translation modes.
- Diagnostics tests should sample counters without clear, sample with clear where intended, read health/resource dump layouts, and verify PPCNT/MPCNT register group decoding.
- Register tests should use read-only/safe registers for broad coverage, and isolate disruptive writes such as link profile, loopback, module admin state, PFC, FEC, and time adjustment behind explicit hardware-lab gating.

For this chunk specifically, a minimal validation signal is that `Docs/researches/chunks/subset-b-005889_research.md` exists and is non-empty, and that no source files, blueprint checklist, or final per-file report were modified by the research worker.

### subset-b-005890: lines 10840-13703

# sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc.h lines 10840-13703

## Scope

This chunk covers the tail of the Mellanox/NVIDIA mlx5 firmware interface header. It is generated ABI description rather than executable code: the structs are bit-accurate command, register, event, capability, and general-object layouts consumed through the `MLX5_GET()`, `MLX5_SET()`, command mailbox, register access, and general object command helpers.

The range starts in the `mtutc` time adjustment register tail, defines port/management/QoS capability access masks, event and command queue records, initial PCI interface and health segment layout, many port and management register documents, flow table root and LAG commands, UMEM/UCTX/MEMIC and software steering object inputs, security offload objects, VHCA migration and page-tracking objects, SyncE/PTP/PCIe congestion objects, and ends with PSP key rotation/SPI generation command formats and the header guard close.

## Purpose

The chunk provides firmware-facing data contracts for mlx5 subsystems that are spread across networking, RDMA, VFIO migration, vDPA, fwctl, devlink, clock/PTP, and hardware steering:

- Capability access masks: `pcam`, `mcam`, `qcam`, and `sbcam` expose which port, management, QoS, and shared-buffer registers/features firmware supports.
- Register documents: port state/counters/buffers/module access, management component update, reset, temperature, real-time clock, PPS, PTP, SyncE, QoS, shared-buffer, and debugging/troubleshooting layouts.
- Command transport primitives: EQE/event payload wrapping, PCIe command queue entry, mailbox block, command input/output headers, and memory translation table entries.
- Firmware boot and health: initial segment fields for firmware revision, command queue address/stride/doorbell, NIC interface mode, health buffer, clear interrupt bit, syndrome, and health counter.
- Resource lifecycles: create/query/modify/destroy style inputs and outputs for flow tables, LAG/vport LAG, MEMIC, UMEM, UCTX, software ICM, Geneve TLV options, subfunctions, general objects, security offload objects, and page tracking.
- Acceleration/security objects: IPsec, MACsec, encryption key, internal KEK, flow meter ASO, sampler, TLS static/progress parameters, PSP key rotation, and PSP SPI/key generation.
- Migration and virtualization: suspend/resume VHCA, query/save/load VHCA state, advanced virtualization caps, page-track object configuration, and dirty-page report entry layout.

## Important APIs, Types, and Data

The capability structs are compact feature-bit maps. `mlx5_ifc_pcam_reg_bits` selects a port feature/access group and returns masks for registers such as `ppcnt`, `pptb`, `pbmc`, `pplm`, and `pphcr`, plus feature bits for FEC rates, buffer ownership, discard/statistical counter groups, connector type, and per-lane/buffer counters. `mlx5_ifc_mcam_reg_bits` similarly exposes management access registers such as `mtmp`, `mfrl`, `mrtc`, tracer registers, `mtutc`, `mpegc`, `mpir`, `mcqs`, `mcqi`, `mcc`, `mcda`, SyncE, `mtptm`, `mtctr`, and `mrtcq`. `mlx5_ifc_qcam_reg_bits` covers QoS registers including QCAP/QPTS/QDPM/QPDPM and trust-state features. `mlx5_ifc_sbcam_reg_bits` adds shared-buffer capability masks and sizing limits.

The command/event ABI includes `mlx5_ifc_eqe_bits`, `mlx5_ifc_cmd_queue_entry_bits`, `mlx5_ifc_cmd_in_bits`, `mlx5_ifc_cmd_out_bits`, `mlx5_ifc_cmd_if_box_bits`, and `mlx5_ifc_mtt_bits`. These define ownership/signature bits, inline command data, mailbox pointer fragments, token/status fields, linked mailbox blocks, and MTT read/write permissions. `mlx5_ifc_initial_seg_bits` is the large MMIO initial segment used during device initialization and health handling.

Port and management registers include PAOS port administrative/operational state, PCAP port capability masks, PCMR CRC/FCS/entropy behavior, PBMC/shared buffer programming, PDDR troubleshooting pages, PPHCR histograms, MTMPS/MTPPSE PPS pin control/events, MCQS/MCQI/MCC/MCDA component update state and data, MFRL firmware reset negotiation, MRTC/MTPTM/MTCTR real-time/PTM timestamp capture, MTMP/MTcap temperature sensors, MCIA module I2C access, ETS/QPTS/QPDPM/PPTB QoS, and SyncE MSECQ/MSEES/MRTCQ layouts.

The register document unions `mlx5_ifc_ports_control_registers_document_bits`, `mlx5_ifc_debug_enhancements_document_bits`, and `mlx5_ifc_uplink_pci_interface_document_bits` provide typed overlays for generic register-access code. The port document union aggregates many layouts defined earlier in the file and in this chunk, with a large reserved fallback so a register payload can be treated as one typed document.

Flow and LAG command structs include `set_flow_table_root`, `modify_flow_table`, `mlx5_ifc_lagc_bits`, `create/modify/query/destroy_lag`, and create/destroy vport LAG command shapes. The `MLX5_MODIFY_FLOW_TABLE_MISS_TABLE_ID` and `MLX5_MODIFY_FLOW_TABLE_LAG_NEXT_TABLE_ID` flags control which flow table context fields are updated. LAG context fields encode FDB selection, port select mode, active port, LAG state, and TX remap affinities.

Memory and user context objects include `modify_memic`, `alloc_memic`, `dealloc_memic`, `mlx5_ifc_umem_bits`, `create/destroy_umem`, `mlx5_ifc_uctx_bits`, `create/destroy_uctx`, `mlx5_ifc_sw_icm_bits`, and `mlx5_ifc_geneve_tlv_option_bits`. These are used by DevX, vDPA, fwctl, software steering, and firmware-managed memory/object allocation paths. UMEM embeds variable-length MTT entries.

General object types and object commands define object IDs for encryption key, IPsec, sampler, flow meter ASO, MACsec, internal KEK, RDMA control, PCIe congestion event, and flow table alias. The chunk provides object body layouts for IPsec ASO and SA state, MACsec ASO and secure channel/association state, encryption keys and wrapped DEKs, internal KEKs, flow meters, samplers, PCIE congestion event thresholds, and command wrappers using `mlx5_ifc_general_obj_in_cmd_hdr_bits` and `mlx5_ifc_general_obj_out_cmd_hdr_bits` from earlier chunks.

Migration and virtualization command types include VHCA suspend/resume, query/save/load migration state, advanced RDMA and virtualization capabilities, page-track report entries, page-track object state/ranges, subfunction partition query, and alloc/dealloc SF commands. These layouts are directly relevant to VFIO live migration and scalable function provisioning.

## Control Flow

This header does not run control flow, but it encodes the control sequences expected by the driver and firmware.

Capability discovery precedes register use. mlx5 core code queries PCAM/MCAM/QCAM/SBCAM groups, then tests individual mask bits before using optional registers or features. For example, port code populates `pcam_reg` and `mcam_reg` selectors, clock code uses MTPPS fields for PPS pin configuration and timestamp reads, and reset code checks MFRL capabilities before negotiating firmware reset levels.

Command submission follows the command queue/mailbox contract. The driver writes `mlx5_ifc_cmd_in_bits` or a command-specific input, may chain `mlx5_ifc_cmd_if_box_bits` mailbox blocks, rings the command doorbell described by the initial segment, and later reads `mlx5_ifc_cmd_out_bits` status/syndrome or command-specific output. EQ handling consumes `mlx5_ifc_eqe_bits` ownership and event type/subtype around the per-event union declared earlier in the file.

Register access is read/modify/write by layout. Many registers contain `field_select`, enable, clear, event-arm, or snapshot bits. Callers must set only intended fields and preserve reserved fields. Examples include MTPPS pin state and pulse duration updates, MTPPSE event arming, MFRL reset negotiation, MSEES SyncE admin fields, shared buffer occupancy clearing, and PDDR troubleshooting page selection.

Object lifecycles are create/query/modify/destroy. LAG is created with a `lagc` context, modified by `field_select`, queried into the same context, and destroyed. General objects are created with object type-specific bodies, queried/modified with matching object IDs, and destroyed by generic commands defined elsewhere. UMEM/UCTX/SF/MEMIC lifecycles allocate firmware IDs or address ranges and later deallocate them explicitly.

Migration flows use ordered state transitions. VHCA migration can suspend initiator or responder, query migration state and required UMEM size, save chunks or incremental state into a supplied VA/mkey/size buffer, load state into a destination VHCA, and resume. Page tracking is configured as a general object with ranges and reporting QP, then modified between tracking/reporting/error states while report entries carry dirty addresses.

Security offload flows combine key objects, ASO state, and steering. Encryption key/internal KEK objects provide key material or wrapped-key handles. IPsec and MACsec objects reference DEK numbers, PDs, salts/IVs/SCI, replay window mode, extended sequence number overlap, ASO return register, lifetime/remove-flow arms, and packet counters. Flow steering and ASO WQEs then act on those object IDs.

## State and Persistence Behavior

Most state described here lives in firmware or device MMIO/register space, not in this header. The structs are the shared schema for mutating and observing that state.

Firmware persistent or semi-persistent state includes reset negotiation in MFRL, component update state/data in MCQS/MCQI/MCC/MCDA, module and port configuration registers, QoS/ETS/trust/DSCP mappings, shared buffer allocation/occupancy watermarks, SyncE administrative tracking, clock/PPS pin configuration, and security key/object contents. Some of these settings affect the device until changed or reset; component update and reset state can outlive an individual driver command.

Resource identity is persistent across the life of each firmware object. Returned or supplied IDs such as `uid`, `umem_id`, `function_id`, `obj_id`, `vhca_id`, QP number, mkey, DEK number, update handle, LAG state/active port, and MEMIC address must be tracked by callers and invalidated on failure, reset, or destroy. UMEM and page tracking additionally depend on host memory remaining pinned/mapped for firmware access.

Counters and event arms are stateful. Buffer occupancy maximums can be cleared, IPsec/MACsec ASO lifetime and remove-flow counters are armed, PPS event generation is explicitly armed, PCIe congestion object thresholds latch event state, and page-track reporting state advances as dirty entries are emitted.

The initial segment is live device state. Fields such as `initializing`, `nic_interface`, command queue physical address, health buffer, `clear_int`, syndrome, and health counter are used during initialization, recovery, and health polling. Incorrect writes to MMIO-backed fields can affect command transport or interrupt/health behavior.

## Dependencies and Integration Points

All layouts depend on mlx5 IFC bitfield conventions: arrays of `u8` with bit widths are not normal C storage fields, and access must go through generated-style helpers such as `MLX5_GET`, `MLX5_SET`, `MLX5_ADDR_OF`, and size macros. Many structs also depend on definitions from earlier chunks, including the event union, health buffer, flow table context, general object headers, flow table property layouts, and many port register layouts referenced by the document union.

Core mlx5 integration points include `drivers/net/ethernet/mellanox/mlx5/core/port.c` for PCAM/MCAM and MTPPSE access, `core/lib/clock.c` for MTPPS/PTP pin control, `core/fw_reset.c` and `core/devlink.c` for MFRL reset levels and types, `core/fs_cmd.c` for flow table modification flags, `core/lag/lag.c` for LAG/vport LAG commands, `core/sf/cmd.c` for subfunction allocation, `core/lib/crypto.c` for encryption-key objects, and `core/en/pcie_cong_event.c` for PCIe congestion event objects.

Accelerator integrations are extensive. IPsec object fields and ASO modes are set by Ethernet IPsec offload code and referenced by hardware steering actions. MACsec object fields, replay window sizes, EPN state, and ASO return register are used by MACsec offload. Flow meter ASO and sampler objects are used by TC offload paths. PSP commands are used by `en_accel/psp.c` to rotate device keys and generate SPI/key tuples.

Userspace-facing and virtualization integrations include RDMA DevX UCTX/UMEM creation, fwctl UCTX usage, vDPA UMEM-backed queues, VFIO mlx5 migration commands for VHCA state and dirty page tracking, and scalable function partition/alloc/dealloc commands used by mlx5 SF support.

Management and diagnostics integrate through devlink, ethtool, PTP hardware clock, thermal/health reporting, firmware update/reset flows, module EEPROM/I2C access, SyncE, and PCIe health/congestion notifications. The port document union ties many of these features to the generic register access transport.

## Risks

ABI drift is the main risk. Every field width, offset, reserved gap, enum value, bit mask, variable-length tail, and union overlay must match firmware. Small layout changes can silently program the wrong firmware field because the generated helpers address by bit offset.

Reserved fields must stay zero unless firmware documents otherwise. Many command/register bodies are mostly reserved bits around a few active fields. Reusing stack or heap buffers without zeroing can send unintended bits to firmware, especially for `field_select`, ASO contexts, reset negotiation, LAG modification, and security objects.

Capability checks are mandatory. Optional bits such as enhanced PCAM/MCAM features, MTPPS extensions, MCIA 32-dword access, SyncE registers, page tracking, IPsec/MACsec/general object types, PCIe congestion events, and SF support must be verified before issuing commands. Assuming support will produce command failures or undefined firmware behavior on older devices.

Firmware-owned IDs and host DMA references are leak-prone. UMEM IDs, UCTX UIDs, object IDs, update handles, SF function IDs, page-track reporting QPs, mkeys, and MEMIC ranges require precise cleanup paths. Host VA/mkey/size fields for migration and UMEM/page tracking must reference valid pinned memory for the whole firmware operation.

Security object handling has high blast radius. IPsec, MACsec, TLS, PSP, encryption key, wrapped DEK, and KEK layouts carry key material, salts, IVs, sequence-number state, replay windows, PDs, and lifetime policy. Wrong key size/purpose, stale DEK number, bad overlap/ESN/EPN state, or incorrect ASO register selection can break traffic security or expose material to the wrong protection domain.

Reset and migration state machines are fragile. MFRL reset states distinguish idle, negotiation, in-progress, timeout, NACK, and unload timeout; devlink and firmware reset paths must map them to user-visible reset behavior. VFIO migration must handle uninitialized, idle, ready, dirty, and init states, and must not treat a zero-size dirty report as success when firmware is still reporting.

Flexible array layouts need careful sizing. `mcqi_reg_bits data[]`, `mcda_reg_bits data[]`, `umem_bits mtt[]`, `query_esw_functions_out_bits host_sf_enable[]`, SF partition arrays, page-track ranges, and PSP `key_spi[]` outputs require callers to allocate command buffers based on element counts and firmware-advertised sizes.

## Test and Validation Signals

Build coverage should compile all mlx5 users with warnings and sparse/endian checks enabled, ensuring member names and generated accessors remain consistent after header regeneration. Because this file is included widely, a layout/member mismatch should break users in Ethernet, RDMA, VFIO, vDPA, fwctl, and core mlx5 code.

ABI validation should compare generated bit offsets and struct sizes against the mlx5 firmware specification for capability masks, initial segment, command queue entry, mailbox block, MFRL, MTPPS/MTPPSE, MCQI/MCC/MCDA, LAG, UMEM/UCTX, IPsec/MACsec, page tracking, PCIe congestion, and PSP command buffers.

Runtime command tests should query PCAM/MCAM/QCAM/SBCAM capabilities before exercising optional registers, then issue representative register reads/writes for PAOS, PBMC/SBPR/SBCM, MTPPS/MTPPSE, MFRL, MTMP, MCIA, QPTS/QPDPM/QETC, SyncE, and PCIe congestion object configuration. Tests should verify status/syndrome handling and that reserved fields are zeroed.

Lifecycle tests should create/query/modify/destroy LAG and vport LAG, UMEM, UCTX, MEMIC, SF allocations, sampler, flow meter ASO, encryption key, IPsec, MACsec, and page-track objects. They should include error cleanup, repeated create/destroy loops, device reset in the middle of lifecycles, and validation that firmware IDs are not reused after destroy by stale driver state.

Security offload tests should cover IPsec replay window sizes, ESN overlap modification, ASO increment-SN and replay-protection modes, hard/soft lifetime/remove-flow arms, MACsec confidentiality/EPN/replay windows, key object purposes and sizes, wrapped-key paths, PSP 128-bit and 256-bit SPI generation, and PSP key rotation failure paths.

Migration tests should run suspend/query/save/load/resume flows for both initiator and responder op-mods, incremental and chunked save modes, required UMEM size changes, short buffer handling, dirty page tracking range setup, reporting state transitions, zero-entry reports, and error-state recovery.

Health and reset tests should validate command queue ownership/signature behavior, initial segment health syndrome/counter polling, clear interrupt behavior, firmware reset negotiation through MFRL levels/types/methods, and devlink-visible reset outcomes for timeout, NACK, and unload-timeout states.

## Cross-Chunk Notes

This chunk depends on earlier `mlx5_ifc.h` chunks for common command headers, capability layouts, event unions, general object headers, flow table context, many port register bodies referenced by the document union, and the bitfield accessor macro ecosystem. The merge lane should synthesize this with prior chunks into one per-file report for `sources/distributed-fs/ceph-client/include/linux/mlx5/mlx5_ifc.h`; this worker intentionally writes only the chunk research document.
