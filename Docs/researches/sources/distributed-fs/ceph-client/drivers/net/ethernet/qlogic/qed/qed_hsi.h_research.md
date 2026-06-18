# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hsi.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-004600`: lines 1-7574, `Docs/researches/chunks/subset-b-004600_research.md`
- `subset-b-004601`: lines 7575-10880, `Docs/researches/chunks/subset-b-004601_research.md`

## Chunk Research

### subset-b-004600: lines 1-7574

# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hsi.h lines 1-7574

## Scope

This chunk covers the first 7,574 lines of `qed_hsi.h`, the QLogic/Marvell QED host/firmware status interface header. It starts at the header guard and common include list, then defines the ABI layouts used by QED slow-path ramrods, event-ring entries, queue contexts, hardware initialization tables, Ethernet vports/queues/filters, TCP offload, generic RDMA, and the beginning of RoCE connection and QP management structures.

The chunk ends inside `struct xstorm_roce_conn_ag_ctx_dq_ext_ld_part`, after `E4XSTORMROCECONNAGCTXDQEXTLDPART_RULE17EN_MASK`. The remaining fields of that RoCE Xstorm dequeue-load partial context, plus later protocols in the file, continue in following chunks and must be reconciled during the final per-file merge.

## Purpose

`qed_hsi.h` is a hardware ABI header, not an ordinary local helper header. Its main purpose is to freeze the exact in-memory and on-DMA-wire layout shared between the Linux QED driver and the firmware running in the device's storm processors. The covered range provides:

- protocol/event opcode numbers for common, core LL2, Ethernet, TOE, RDMA, and RoCE slow-path completions;
- ramrod payload structures that the driver DMA-writes and firmware consumes for PF/VF start, queue start/stop/update, filter programming, vport updates, RDMA memory registration, CQ/SRQ operations, TOE offload, and RoCE QP operations;
- completion, event-ring, CQE, BD, doorbell, stats, and VF-zone structures that firmware writes back or polls;
- storm context layouts for Xstorm, Ystorm, Pstorm, Tstorm, Mstorm, and Ustorm aggregate/state contexts;
- init-tool metadata, runtime-array offsets, QM/BRB/NIG/PBF/CDU/ILT init parameters, and prototypes for QED init helpers implemented elsewhere.

Most fields are explicitly little-endian (`__le16`, `__le32`) or hardware register pairs (`struct regpair`). That is a key part of the ABI: the driver must fill these structures in the firmware-defined byte order and size, not in host-native layout assumptions.

## Important APIs, Types, and Constants

### Common, Core LL2, and Event Ring

The early chunk defines `common_event_opcode`, `common_ramrod_cmd_id`, `core_event_opcode`, and `core_ramrod_cmd_id` for common PF/VF lifecycle and light-L2 queue operations. The core LL2 surface includes:

- queue stats structures such as `core_ll2_port_stats`, `core_ll2_rx_per_queue_stat`, and `core_ll2_tx_per_queue_stat`;
- RX/TX descriptors and CQEs: `core_rx_bd`, `core_rx_bd_with_buff_len`, `core_rx_fast_path_cqe`, `core_rx_gsi_offload_cqe`, `core_rx_slow_path_cqe`, `core_tx_bd`, and associated unions;
- ramrod payloads: `core_rx_start_ramrod_data`, `core_rx_stop_ramrod_data`, `core_tx_start_ramrod_data`, `core_tx_stop_ramrod_data`, `core_tx_update_ramrod_data`, and `core_queue_stats_query_ramrod_data`;
- bitfield masks for LL2 producer updates, RX error actions, TX checksum/VLAN/offload flags, TX destination, and L4 header offsets.

`event_ring_entry`, `event_ring_data`, and `event_ring_element` define the shared asynchronous completion format. Event entries carry `protocol_id`, `opcode`, `vf_id`, `echo`, `fw_return_code`, an async flag, and a protocol-specific 8-byte data union for VF/PF channel messages, iSCSI/RDMA events, initial cleanup, and firmware errors.

### PF/VF Lifecycle, DCB, Tunnels, and VF Zones

`pf_start_ramrod_data`, `pf_update_ramrod_data`, `vf_start_ramrod_data`, and `vf_stop_ramrod_data` are the common lifecycle payloads. PF start carries event-ring PBL addresses, consolidated queue PBL information, tunnel configuration, base VF allocation, personality, MF mode, firmware HSI version, outer-tag policy, and error mode. PF update carries DCB/DSCP updates for Ethernet, FCoE, iSCSI, RoCE, RRoCE, and iWARP plus tunnel and MF VLAN updates.

VF-zone structures split firmware-visible data into non-triggering stats/producers and triggering message-valid fields: `mstorm_vf_zone`, `pstorm_vf_zone`, `tstorm_vf_zone`, `ustorm_vf_zone`, and `xstorm_vf_zone`. These are integration points for SR-IOV PF/VF communication and per-VF statistics.

### DMAE, IGU, PRS, QM, SDM, and Init Tool

The hardware/register-control section defines:

- `dmae_cmd` plus enums for DMAE source, destination, completion, CRC, and error handling;
- `qed_dmae_params`, which is a driver-facing parameter block for DMAE operations and VF/PF attribution;
- IGU interrupt command formats: `igu_cleanup`, `igu_command`, `igu_command_reg_ctrl`, `igu_mapping_line`, and `igu_msix_vector`;
- parser encapsulation enable flags in `prs_reg_encapsulation_type_en`;
- QM/PXP/SDM register formats such as `qm_rf_bypass_mask`, `qm_rf_opportunistic_mask`, `qm_rf_pq_map`, `sdm_agg_int_comp_params`, and `sdm_op_gen`;
- generic host memory descriptors `phys_mem_desc` and `virt_mem_desc`.

The init-tool ABI includes BRB, ETS, NIG, and QM parameter records (`init_brb_ram_req`, `init_ets_req`, `init_nig_lb_rl_req`, `init_qm_*`), init mode/phase/split enums, binary init buffer headers, firmware version/overlay metadata, init operation encodings (`init_write_op`, `init_read_op`, `init_if_mode_op`, `init_if_phase_op`, `init_callback_op`, `init_delay_op`), and `union init_op`.

The `*_RT_OFFSET` and `*_RT_SIZE` macros define the runtime array ABI used by generated init code. They include DORQ, IGU, CAU, PRS, SRC, PSWRQ2/ILT, PGLUE, TM, QM, NIG, CDU, PBF, and XCM offsets and end this chunk's init table at `RUNTIME_ARRAY_SIZE 34984`. These constants are state indices into the runtime-init array, not register addresses by themselves.

### Exported Helper Prototypes

Unlike most of the chunk, lines around 2401-2742 declare actual driver helper functions implemented elsewhere:

- QM sizing/init: `qed_qm_pf_mem_size`, `qed_qm_common_rt_init`, `qed_qm_pf_rt_init`;
- rate and scheduling controls: `qed_init_pf_wfq`, `qed_init_pf_rl`, `qed_init_vport_wfq`, `qed_init_vport_tc_wfq`, `qed_init_global_rl`, `qed_send_qm_stop_cmd`;
- tunnel and GFT programming: `qed_set_vxlan_dest_port`, `qed_set_vxlan_enable`, `qed_set_gre_enable`, `qed_set_geneve_dest_port`, `qed_set_geneve_enable`, `qed_set_vxlan_no_l2_enable`, `qed_gft_disable`, `qed_gft_config`;
- diagnostics/string/error helpers: `qed_get_protocol_type_str`, `qed_get_ramrod_cmd_id_str`, `qed_set_rdma_error_level`;
- overlay memory lifecycle: `qed_fw_overlay_mem_alloc`, `qed_fw_overlay_init_ram`, `qed_fw_overlay_mem_free`.

These prototypes take `struct qed_hwfn *` and often `struct qed_ptt *`, tying the HSI declarations to the QED hardware-function object and register-window access path.

### Ethernet Contexts, Queues, Vports, and Filters

The Ethernet section starts at `tstorm_eth_conn_st_ctx` and defines a full `eth_conn_context` made from storm-specific state and aggregate contexts. The Xstorm/Tstorm/Ustorm/Ystorm/Mstorm aggregate contexts carry producer/consumer indices, state bits, completion flags, slow-path flags, flush flags, EDPM controls, TPH controls, queue IDs, and interrupt coalescing values. The repeated `*_MASK`/`*_SHIFT` definitions are the only safe way for driver code or generated context code to set individual context bits.

Ethernet slow-path definitions include:

- `eth_error_code`, `eth_event_opcode`, `eth_ramrod_cmd_id`, and `eth_return_code`;
- filter records: `eth_filter_cmd`, `eth_filter_cmd_header`, `eth_filter_type`, `vport_filter_update_ramrod_data`;
- vport mode/config records: `eth_vport_rx_mode`, `eth_vport_tx_mode`, `eth_vport_tpa_param`, `eth_vport_rss_config`, and `eth_in_to_in_pri_map_cfg`;
- queue ramrods: `rx_queue_start_ramrod_data`, `rx_queue_stop_ramrod_data`, `rx_queue_update_ramrod_data`, `tx_queue_start_ramrod_data`, `tx_queue_stop_ramrod_data`, and `tx_queue_update_ramrod_data`;
- flow steering/OpenFlow/GFT/UDP filter payloads: `rx_create_gft_action_ramrod_data`, `rx_create_openflow_action_ramrod_data`, `rx_openflow_filter_ramrod_data`, `rx_udp_filter_ramrod_data`, and `rx_update_gft_filter_ramrod_data`;
- vport lifecycle payloads: `vport_start_ramrod_data`, `vport_stop_ramrod_data`, `vport_update_ramrod_data_cmn`, `vport_update_ramrod_mcast`, and `vport_update_ramrod_data`.

The Ethernet ramrods integrate vport state, RSS tables/keys, multicast bins, TPA/GRO settings, VLAN stripping/remapping, anti-spoofing, control-frame checks, destination-vport forwarding, PMD mode, TPH steering, completion behavior, and PBL/BD/CQE addresses.

### GFT Parser/Profile Data

`gft_cam_line_mapped`, `gft_profile_key`, `gft_ram_line`, and related enums describe Generic Flow Table matching. They model protocol keys, tunnel types, IP version, upper protocol class, PF ID matching, VLAN selection, and per-field match masks for inner/outer tunnel and non-tunnel headers. This is the parser/searcher ABI used by GFT filter setup rather than a software hash table.

### RDMA Task, Generic RDMA, TOE, and RoCE

The RDMA task context section defines `rdma_task_context` from Ystorm/Mstorm/Ustorm/Tstorm task contexts. These carry task validity, connection type, DIF flags, reference counts, FBO, parent MR, and hardware scheduler bits.

The TOE section defines `toe_conn_context`, init/offload/update ramrods, RX/TX descriptors and CQEs, GRQ descriptors, application buffer descriptors, page-pointer BDs/CQEs, doorbell data, and TOE opcode enums. It integrates with `tcp_common.h` through embedded `tcp_init_params`, `tcp_offload_params`, and `tcp_update_params`.

The generic RDMA section defines CNQ/CQ/SRQ/TID ramrods and opcodes:

- `rdma_init_func_ramrod_data`, `rdma_close_func_ramrod_data`, `rdma_cnq_params`;
- `rdma_create_cq_ramrod_data`, `rdma_resize_cq_ramrod_data`, `rdma_destroy_cq_ramrod_data` and output params;
- `rdma_register_tid_ramrod_data`, `rdma_deregister_tid_ramrod_data`, and `rdma_tid_type`;
- `rdma_srq_create_ramrod_data`, `rdma_srq_modify_ramrod_data`, `rdma_srq_destroy_ramrod_data`, `rdma_srq_context`, and `rdma_xrc_srq_context`;
- `rdma_event_opcode`, `rdma_ramrod_cmd_id`, and `rdma_fw_return_code`.

The RoCE section, continuing to the chunk end, defines `roce_conn_context`, RoCE QP create/modify/query/destroy/suspend/resume data, RoCE CQE/stat structures, DCQCN parameters, LL2 CQE data, and event/ramrod opcode enums. Requester and responder ramrods are split (`roce_create_qp_req_ramrod_data`, `roce_create_qp_resp_ramrod_data`, `roce_modify_qp_req_ramrod_data`, `roce_modify_qp_resp_ramrod_data`) and include QP IDs, PD, CQ CIDs, P_Key, GIDs, PSNs, retry/RNR/timeout controls, physical queues, SRQ/XRC flags, and force-loopback/EDPM/VF-valid flags.

## Control Flow

There is very little executable control flow in this chunk because it is mostly declarations. Runtime control flow is implicit in the ramrod protocol:

1. Driver code allocates DMA-visible memory and fills one of these payload structures with little-endian fields.
2. The driver posts a slow-path element (`slow_path_element`/`ramrod_header`) or rings a doorbell using protocol and command IDs from this header.
3. Firmware reads the payload, mutates storm connection contexts, queue producers/consumers, filter tables, QM runtime state, parser/GFT state, or protocol offload state.
4. Firmware reports completion through an event-ring entry, CQE, return-code field, status block, or output-params DMA buffer.

For initialization, generated init code uses `union init_op`, init buffer metadata, mode/phase predicates, and `*_RT_OFFSET` indices to populate a runtime array and write device registers through helpers declared in this header. For queueing and offload protocols, producer/consumer fields and context flags represent the effective state machine, while actual transitions are implemented in firmware and QED C files outside this header.

## State and Persistence Behavior

State represented here is persistent hardware/firmware state, not persistent local software state in the header. Important state categories include:

- PF/VF lifecycle state: PF start/update parameters, VF start/stop data, VF-zone message-valid bits, base VF ranges, personality, MF mode, and HSI version.
- Queue state: RX/TX PBL base addresses, BD/CQE producers and consumers, queue IDs, status block IDs/indices, TPH/PMD/notification flags, and completion policies.
- Filter/vport state: MAC/VLAN/VNI filters, OpenFlow/GFT/UDP filters, RSS keys and indirection tables, multicast bins, anti-spoofing, default VLAN handling, inner VLAN removal/remapping, and TPA/GRO settings.
- Init/runtime state: runtime array values for DORQ/IGU/CAU/PRS/SRC/ILT/TM/QM/NIG/CDU/PBF, plus QM WFQ/RL/VOQ/PQ maps and global/vport/PF rate-limit credits.
- Protocol offload state: TOE TCP offload buffers and doorbells, RDMA TIDs/CQs/SRQs/CNQs, RoCE QP request/response state, suspended QP runtime data, RDB entries, DCQCN config, and RoCE error/event stats.
- Firmware event/error state: event-ring opcodes, return codes, firmware error scope/ID, and per-protocol completion data.

Many structures include `reserved` fields. Those are part of the ABI and should normally be zero-filled by the driver unless the firmware contract says otherwise. Reusing or failing to clear reserved fields risks undefined firmware behavior across chip or firmware revisions.

## Dependencies and Integration Points

This header depends on Linux core types and QED protocol HSI headers: `common_hsi.h`, `storage_common.h`, `tcp_common.h`, `fcoe_common.h`, `eth_common.h`, `iscsi_common.h`, `nvmetcp_common.h`, `iwarp_common.h`, `rdma_common.h`, `roce_common.h`, and `qed_fcoe_if.h`. Many array sizes and embedded types, such as `NUM_OF_TCS`, `NUM_STORMS`, `ETH_RSS_IND_TABLE_ENTRIES_NUM`, `RDMA_MAX_IRQ_ELEMS_IN_PAGE`, `struct timers_context`, `struct rdma_srq_id`, and TCP/RDMA/RoCE common parameter records, come from those headers.

The declarations integrate with the rest of the QED driver through:

- slow-path queue code that constructs `slow_path_element` and protocol ramrod payloads;
- queue/vport/filter code that interprets Ethernet opcodes, return codes, and filter errors;
- init code that consumes runtime-array offsets and calls the `qed_qm_*`, tunnel, GFT, and overlay functions declared here;
- interrupt/event-ring code that decodes `event_ring_entry` and protocol-specific data unions;
- SR-IOV code that maps VF zones and VF/PF channel data;
- RDMA/RoCE/iWARP/TOE code that shares connection contexts, task contexts, CQs, SRQs, TIDs, QPs, and protocol completions with firmware;
- generated firmware/context initialization code that expects exact struct field order, size, and mask definitions.

## Risks and Edge Cases

- ABI drift is the central risk. Any field reorder, type-width change, enum renumbering, or mask/shift edit can break communication with firmware even if the C compiler accepts the code.
- Endianness is explicit. Host code must use the correct `cpu_to_le16/32` style conversions before DMAing structures to firmware and must convert firmware-written values when reading them.
- Packedness is implicit through careful scalar choices and reserved padding, not through a visible `__packed` on every structure. Build-time size/offset checks in adjacent code are important when compilers or included types change.
- Many flag words contain active bits adjacent to reserved bits. Read/modify/write users must mask carefully and preserve or clear only the intended bits.
- The runtime-array offsets are generated constants. Hand edits, partial regenerations, or mismatches with firmware/init blobs can write the wrong hardware register values.
- Event, ramrod, and return-code enums are protocol contracts. Reusing values or assuming dense compatibility across protocols can route completions to the wrong handler.
- The chunk boundary cuts through a RoCE aggregate context. Consumers of this chunk alone do not have a complete definition for `xstorm_roce_conn_ag_ctx_dq_ext_ld_part`.

## Test and Validation Signals

Useful validation for this chunk is mostly build-time, firmware-interface, and hardware-integration oriented:

- compile coverage of all QED configurations that include Ethernet, SR-IOV, RDMA/RoCE, TOE/iWARP, FCoE, iSCSI, and NVMf/TCP headers;
- static assertions or generated checks comparing structure sizes, offsets, enum values, and context-layout hashes against firmware HSI expectations;
- sparse/endian checking for assignments into `__le16`/`__le32` fields;
- init-path tests that verify `RUNTIME_ARRAY_SIZE` and representative `*_RT_OFFSET`/`*_RT_SIZE` ranges are in bounds and match generated init blobs;
- slow-path tests or hardware smoke tests for PF start/update, VF start/stop, RX/TX queue start/stop/update, vport start/update/stop, filter updates, and event-ring completions;
- RDMA/RoCE tests that exercise MR registration, CQ/SRQ create/resize/destroy, QP create/modify/query/destroy/suspend/resume, DCQCN update, and RoCE LL2 CQE handling;
- negative-path tests for filter table full/duplicate/not-found errors, MTU/BD/VLAN violations, firmware error event decoding, and ramrod return-code mapping.

## Cross-Chunk Notes

This is a partial research artifact for `qed_hsi.h`. Later chunks must complete the tail of `xstorm_roce_conn_ag_ctx_dq_ext_ld_part` and cover the remaining iWARP/iSCSI/FCoE/NVMf/TCP or other protocol layouts after line 7,574. The final merge lane should synthesize one source-tree-aligned report for the whole header and should explicitly note that this file is a generated/firmware-coupled ABI surface rather than ordinary handwritten algorithmic code.

### subset-b-004601: lines 7575-10880

# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_hsi.h lines 7575-10880

## Chunk Scope

This chunk is the tail of the QED hardware/software interface header. It is not
executable driver logic; it defines the host-visible ABI layouts shared by the
Linux QED driver and the QLogic/Marvell firmware for RDMA storage offloads and
related TCP-based protocols. The range starts in the final fields of an E4
Xstorm RoCE aggregation context, continues through RoCE request/response
aggregation contexts, then defines iWARP connection contexts, iWARP ramrod and
event payloads, FCoE connection contexts and ramrod/event identifiers, and the
first iSCSI connection context definitions before the header guard closes.

The definitions are source-tree critical because `qed_cxt.c` uses the context
types in the global connection-context union, `qed_sp.h` embeds the ramrod
payload types in the slow-path command union, and protocol modules such as
`qed_iwarp.c`, `qed_roce.c`, `qed_ll2.c`, and `qed_fcoe.c` fill or interpret
these structures when posting commands to firmware.

## Purpose and Responsibilities

- Publish exact little-endian memory layouts for firmware-owned connection
  contexts in Mstorm, Tstorm, Ustorm, Xstorm, Ystorm, and Pstorm.
- Provide bit-mask and shift constants for compact `u8`/`__le16` flag fields,
  including condition flags, enable bits, rule gates, queue-manager membership,
  flush/error state, producer/consumer threshold tracking, and protocol feature
  toggles.
- Define the `roce_flavor` selector used by RoCE packet handling for plain
  RoCE and routable RoCE over IPv4/IPv6.
- Define iWARP control-plane payloads for TCP offload, MPA offload, create QP,
  modify/query/destroy/abort command identifiers, async/sync EQE opcodes, and
  firmware return codes.
- Define FCoE static and aggregation contexts for each storm engine, including
  Ethernet/VLAN encapsulation state, queue PBL addresses, FC IDs, timers,
  protection-information bits, cached WQEs, and ramrod wrapper/event enums.
- Define iSCSI connection context fragments at the end of the header, including
  combined TCP/iSCSI storm contexts and aggregation contexts for Xstorm,
  Tstorm, Ustorm, Mstorm, and Ystorm.

## Important APIs, Types, and Constants

- RoCE aggregation contexts:
  `mstorm_roce_conn_ag_ctx`, `mstorm_roce_req_conn_ag_ctx`,
  `mstorm_roce_resp_conn_ag_ctx`, `tstorm_roce_req_conn_ag_ctx`,
  `tstorm_roce_resp_conn_ag_ctx`, `ustorm_roce_req_conn_ag_ctx`,
  `ustorm_roce_resp_conn_ag_ctx`, `xstorm_roce_req_conn_ag_ctx`,
  `xstorm_roce_resp_conn_ag_ctx`, `ystorm_roce_conn_ag_ctx`,
  `ystorm_roce_req_conn_ag_ctx`, and `ystorm_roce_resp_conn_ag_ctx`.
  These structures expose per-QP firmware scheduler state: `state`,
  `physical_q0`, `conn_dpi`, send/request queue consumers and producers,
  retransmit PSNs, ACK/IRQ tracking, DIF counters and error offsets, ORQ
  fences, responder RXMIT data, and flush/error condition flags.
- `enum roce_flavor`: identifies `PLAIN_ROCE`, `RROCE_IPV4`, and
  `RROCE_IPV6`. Nearby driver code maps public RoCE mode to this enum and LL2
  transmit code maps LL2 packet flavor to core BD fields.
- iWARP connection storage:
  `ystorm_iwarp_conn_st_ctx`, `pstorm_iwarp_conn_st_ctx`,
  `xstorm_iwarp_conn_st_ctx`, `tstorm_iwarp_conn_st_ctx`,
  `mstorm_iwarp_conn_st_ctx`, `ustorm_iwarp_conn_st_ctx`,
  `xstorm_iwarp_conn_ag_ctx`, `tstorm_iwarp_conn_ag_ctx`,
  `mstorm_iwarp_conn_ag_ctx`, `ustorm_iwarp_conn_ag_ctx`, and
  `ystorm_iwarp_conn_ag_ctx`. `struct iwarp_conn_context` assembles these into
  the complete connection context allocated through the CDU/ILT context path.
- iWARP ramrod payloads:
  `iwarp_create_qp_ramrod_data` contains QP creation flags for FMR/reserved
  LKey, signaled completions, RDMA read/write, atomics, SRQ, and low-latency
  queue enablement plus PD, SQ/RQ page counts, CQ CIDs, DPI, physical queues,
  QP handle, and SRQ ID.
  `iwarp_tcp_offload_ramrod_data` combines `tcp_offload_params_opt2` with
  `iwarp_offload_params` for TCP connection offload.
  `iwarp_mpa_offload_ramrod_data` carries MPA private-data buffers, TCP CID,
  negotiation mode, active/passive side, RTR preferences, async output buffers,
  shared queue address, receive window, and stats counter.
  `iwarp_modify_qp_ramrod_data`, `iwarp_query_qp_ramrod_data`, and
  `iwarp_query_qp_output_params` define state transition and query ABI.
- iWARP event and status enums:
  `iwarp_eqe_async_opcode` reports connect complete, MPA reply/request,
  handshake complete, cleaned CID, exception, QP error, CQ overflow, and SRQ
  limit/empty events. `iwarp_eqe_sync_opcode` and `iwarp_ramrod_cmd_id` use the
  same command numbering for TCP offload, MPA offload, create/query/modify/
  destroy QP, and abort TCP offload. `iwarp_fw_return_code` enumerates TCP,
  MPA, QP error, and exception causes reported by firmware.
- MPA helpers:
  `mpa_rq_params`, `mpa_ulp_buffer`, `mpa_outgoing_params`,
  `mpa_negotiation_mode`, and `mpa_rtr_type` define Basic/Enhanced MPA private
  data and RTR negotiation fields. `unaligned_opaque_data` describes LL2 data
  used when initial MPA bytes arrive unaligned in TCP payloads.
- FCoE contexts:
  `ystorm_fcoe_conn_st_ctx`, `pstorm_fcoe_conn_st_ctx`,
  `xstorm_fcoe_conn_st_ctx`, `ustorm_fcoe_conn_st_ctx`,
  `tstorm_fcoe_conn_st_ctx`, `mstorm_fcoe_conn_st_ctx`, and their aggregation
  contexts form `struct fcoe_conn_context`. These include FC payload sizes,
  MTU/MSS, source/destination FC IDs, Ethernet MAC/VLAN fields, SQ/XFERQ/RESPQ
  PBLs and indices, cached `fcoe_wqe` entries, queue producers/consumers,
  BDQ/CQ/CMDQ relative offsets, timers, and protection metadata.
- FCoE ramrod/event wrappers:
  `fcoe_conn_offload_ramrod_params`, `fcoe_conn_terminate_ramrod_params`,
  `fcoe_init_ramrod_params`, and `fcoe_stat_ramrod_params` wrap earlier FCoE
  payload definitions. `enum fcoe_event_type` and `enum fcoe_ramrod_cmd_id`
  enumerate init, destroy, stat, offload connection, terminate connection, and
  error flows.
- iSCSI context tail:
  `ystorm_iscsi_conn_st_ctx`, `pstorm_iscsi_tcp_conn_st_ctx`,
  `xstorm_iscsi_tcp_conn_st_ctx`, `xstorm_iscsi_conn_ag_ctx`,
  `tstorm_iscsi_conn_ag_ctx`, `ustorm_iscsi_conn_ag_ctx`,
  `tstorm_iscsi_conn_st_ctx`, `mstorm_iscsi_conn_ag_ctx`,
  `mstorm_iscsi_tcp_conn_st_ctx`, `ustorm_iscsi_conn_st_ctx`,
  `iscsi_conn_context`, `iscsi_init_ramrod_params`, and
  `ystorm_iscsi_conn_ag_ctx`. These complete the header with TCP/iSCSI
  offload state and iSCSI init parameters.

## Control Flow and Firmware Protocol Flow

This header chunk has no functions, branches, or loops, but it encodes control
flow as firmware state-machine fields:

- Queue-manager residency bits such as `EXIST_IN_QM0` through `EXIST_IN_QM3`
  tell firmware scheduler logic whether the connection currently has work in a
  physical queue.
- `state` bytes in Xstorm/Tstorm/Mstorm contexts are firmware connection-state
  slots. Driver code normally initializes or transitions them indirectly by
  posting ramrods instead of writing state-machine code in the host.
- Two-bit condition fields (`*_CF*`, `*_FLUSH_*`, `*_RX_ERROR_*`,
  `*_TIMER_STOP_ALL_*`, `*_SLOW_PATH`, and similar) pair with one-bit enable
  fields (`*_CF*_EN`, `*_RULE*EN`) to let firmware evaluate events, timers,
  queue thresholds, and protocol-specific decision rules.
- RoCE request contexts coordinate send queue advancement, retransmit and PSN
  state, DIF error accounting, ORQ fences, invalidation fences, max-ORD
  gating, eDPM enablement, and migration flags. Responder contexts coordinate
  RQ/IRQ producer-consumer state, force ACK/retransmit work, RX/TX error
  signals, and syndrome reporting.
- iWARP TCP offload proceeds through a slow-path command using
  `iwarp_tcp_offload_ramrod_data`; later MPA negotiation uses
  `iwarp_mpa_offload_ramrod_data`; then QP creation and modifications use the
  QP ramrod payloads. The async EQE opcodes and firmware return codes in this
  chunk are the completion/error side of that protocol flow.
- FCoE offload uses `fcoe_init_ramrod_params` for function setup, per-connection
  `fcoe_conn_offload_ramrod_params` and `fcoe_conn_context` for offloaded FC
  exchanges, and terminate/stat ramrods for cleanup and accounting. The Xstorm
  FCoE aggregation context contains SQ/XFERQ/RESPQ decision enables, which are
  firmware-side control points for deciding which FC queue can progress.
- iSCSI offload state at the end mirrors the same pattern: a combined TCP/iSCSI
  static context plus storm aggregation contexts with flush, cleanup, queue
  decision, and slow-path bits.

## State and Persistence Behavior

The state represented here is persistent hardware/firmware connection context
state, not ordinary kernel heap-only state. QED allocates connection contexts
through the context manager (`qed_cxt.c`) and stores them in CDU/ILT-backed
memory visible to firmware. The `union conn_context` in `qed_cxt.c` includes
`roce_conn_context`, `iwarp_conn_context`, `fcoe_conn_context`, and
`iscsi_conn_context`; therefore the size and alignment of these structs directly
affect context allocation, ILT sizing, and firmware indexing.

Fields use fixed-width kernel types and little-endian annotations such as
`__le16`, `__le32`, and `struct regpair`. Host code must convert CPU values
with `cpu_to_le16()`, `cpu_to_le32()`, `DMA_REGPAIR_LE()`, `DMA_LO_LE()`, and
`DMA_HI_LE()` before posting ramrods or programming DMA addresses. The layouts
also contain explicit padding (`reserved`, `*_padding`, `e5_reserved`,
`a0_reserved`) to preserve firmware ABI offsets across chip generations and
firmware revisions.

Many producer/consumer fields are long-lived connection progress markers:
RoCE `sq_cons`, `sq_prod`, `rq_cons`, `rq_prod`, `irq_cons`, `irq_prod`,
`snd_una_psn`, `snd_nxt_psn`, and ORQ counters; iWARP `sq_tx_cons`,
`irq_cons`, `hq_cons`, `orq_cons`, and shared queue page addresses; FCoE
`sq_cons`, `sq_prod`, `xferq_prod`, `xferq_cons`, `respq_prod`, `respq_cons`,
PBL current/next page addresses, and cached WQEs; iSCSI SQ/R2TQ/HQ producer
and consumer values. These values persist for the life of an offloaded
connection and are consumed by firmware across interrupts, timers, retransmit
events, and slow-path commands.

## Dependencies and Integration Points

- `qed_hsi.h` depends on earlier declarations in the same header, including
  `regpair`, `timers_context`, `rdma_init_func_ramrod_data`,
  `tcp_init_params`, `tcp_offload_params_opt2`, `rdma_srq_id`,
  `fcoe_wqe`, `fcoe_conn_offload_ramrod_data`,
  `fcoe_conn_terminate_ramrod_data`, `fcoe_init_func_ramrod_data`,
  `fcoe_stat_ramrod_data`, `pb_context`, and `iscsi_spe_func_init`.
- `qed_cxt.c` consumes `iwarp_conn_context`, `fcoe_conn_context`, and
  `iscsi_conn_context` in `union conn_context`, so any layout change affects
  CDU context sizing and the ILT memory model.
- `qed_sp.h` embeds `iwarp_create_qp_ramrod_data`,
  `iwarp_tcp_offload_ramrod_data`, and `iwarp_mpa_offload_ramrod_data` in the
  slow-path ramrod union; `qed_iwarp.c` fills those payloads with DMA buffer
  addresses, endpoint handles, physical queues, TCP 4-tuple data, MPA mode,
  RTR preferences, and QP capability bits before calling `qed_spq_post()`.
- `qed_iwarp.c` also interprets the MPA async output and uses the MPA enums in
  this chunk to negotiate Basic versus Enhanced MPA, ORD/IRD, and RTR type
  behavior.
- `qed_fcoe.c` posts FCoE init/offload/terminate/stat ramrods and obtains
  `fcoe_conn_context` information through the context manager while validating
  PF FCoE parameters such as CQ counts, MTU, PBL pages, timers, and physical
  queues.
- `qed_roce.c` maps higher-level RoCE mode to `enum roce_flavor`, while
  `qed_ll2.c` uses RoCE flavor information when constructing transmit BD data
  for LL2 RoCE packets.
- Firmware is the most important integration point. The comments name these
  structures as "passed by driver to FW" or "storm context" layouts. The host
  driver and firmware must agree on every offset, width, endian conversion, and
  reserved bit convention.

## Risks and Edge Cases

- ABI drift is the dominant risk. Reordering a field, changing a type width,
  removing padding, or altering a mask/shift constant can silently corrupt
  firmware context interpretation even if the C code still compiles.
- Reserved bits are not free. Many fields carry `A0_RESERVED`, `E5_RESERVED`,
  or generic `RESERVED` names. Driver code should preserve zeros unless a
  matching firmware contract explicitly assigns meaning to the bit.
- Endian mistakes are easy because the structs mix `u8` flags with `__le16`,
  `__le32`, and `regpair` values. A missing `cpu_to_le*()` conversion in code
  that fills these ramrods may work on little-endian hosts and fail on
  big-endian configurations.
- The condition-flag and enable-bit pairs are dense. Using a mask from the
  request side on a responder context, or from RoCE on iWARP/FCoE/iSCSI, can
  enable an unrelated firmware rule because the fields intentionally reuse
  compact bit positions.
- Context sizing is cross-protocol. Because `union conn_context` takes the
  maximum of these layouts, growth in FCoE/iWARP/iSCSI contexts can affect ILT
  allocation and memory pressure for all connection types.
- Several `enum` values start at nonzero offsets, especially iWARP synchronous
  opcodes and ramrod command IDs starting at 13. Code must use symbolic enums
  rather than assuming dense zero-based command numbering.
- Fields such as shared queue page addresses, PBL addresses, async EQE output
  buffers, and ULP private-data buffers are DMA contracts. The host must keep
  those buffers mapped, aligned, and alive until firmware completion or cleanup
  guarantees they are no longer referenced.
- Protocol boundaries are adjacent in one header. The chunk moves from RoCE to
  iWARP to FCoE to iSCSI, so broad search-and-replace edits or generated mask
  updates can accidentally modify similarly named fields in the wrong protocol.

## Test Signals and Validation Hooks

- Compile-time coverage should include all protocol objects that include
  `qed_hsi.h`: at minimum QED core context management, RDMA/iWARP, RoCE LL2,
  FCoE, and iSCSI-enabled builds. Header-only ABI changes should be treated as
  requiring broad driver rebuilds, not protocol-local rebuilds.
- Static layout checks are valuable when available: compare `sizeof()` and
  `offsetof()` for `iwarp_conn_context`, `fcoe_conn_context`,
  `iscsi_conn_context`, and important ramrod structs against firmware HSI
  expectations.
- Runtime iWARP signals include successful TCP offload, MPA offload,
  create-QP/modify-QP/query-QP flows, correct async EQE decoding for connect,
  MPA, CID-cleaned, exception, CQ overflow, and SRQ limit/empty events, and
  correct mapping of firmware return codes to upper RDMA CM errors.
- Runtime RoCE signals include correct RoCE flavor selection, successful QP
  send/receive traffic, retransmit/force-ACK behavior, error flush completion,
  and no corruption of PSN, ORQ, IRQ, SQ, or RQ producer-consumer state.
- Runtime FCoE signals include init/offload/terminate/stat ramrod completion,
  correct VLAN/MAC/FC ID programming, queue producer-consumer progress for SQ,
  XFERQ, RESPQ, CQ, CMDQ, and BDQ resources, protection-info behavior, and
  cleanup after timers or error paths.
- Runtime iSCSI signals include successful context allocation for TCP/iSCSI
  connections, cleanup/flush completion, queue decision rule progress, checksum
  error accounting, and stable SQ/R2TQ/HQ producer-consumer tracking.
- Diagnostic output in protocol modules is a useful smoke signal: iWARP debug
  prints expose fields filled from `iwarp_tcp_offload_ramrod_data`, while FCoE
  start paths validate PF parameters before posting ramrods. Any mismatch
  between debug values and expected host configuration points to a ramrod
  population or endian/layout issue.
