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
