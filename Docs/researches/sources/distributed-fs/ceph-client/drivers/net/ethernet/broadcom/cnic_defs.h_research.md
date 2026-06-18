# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/cnic_defs.h

## Purpose
`cnic_defs.h` is a firmware/hardware ABI header for the Broadcom/QLogic CNIC storage-offload path used by the Ceph-client kernel source snapshot. It defines the kernel work queue entries, kernel completion queue entries, per-storm firmware contexts, FCoE task and connection records, iSCSI PDU/task/connection records, TCP offload context fragments, and L5 connection-manager/passive-open structures consumed by the CNIC driver and related Broadcom Ethernet drivers.

The file is not algorithmic application code. It is a layout contract between host driver code, DMA memory, and on-chip firmware. Most structures are deliberately shaped with `__BIG_ENDIAN`/`__LITTLE_ENDIAN` conditional member order, fixed-width integer fields, and companion mask/shift macros. A driver change that looks like ordinary C cleanup can break the device ABI.

## Important APIs, Types, and Functions
There are no functions. The public API is the set of opcodes, completion statuses, bit masks, enums, unions, and C structs used to build firmware commands and interpret completions.

The top-level command families include `L2_KWQE_OPCODE_VALUE_*`, `L4_KWQE_OPCODE_VALUE_*`, `L5CM_RAMROD_CMD_ID_*`, `FCOE_RAMROD_CMD_ID_*`, `L4_KCQE_OPCODE_VALUE_*`, and `L4_KCQE_COMPLETION_STATUS_*`. These identify flush/free operations, TCP connect/reset/close/update/init operations, page/offload operations, L5 connection manager ramrods, FCoE init/stat/connection ramrods, and KCQ completion classes.

L4/TCP work and completion entries include `struct l4_kcq`, `struct l4_kcq_upload_pg`, `struct l4_kwq_close_req`, `struct l4_kwq_connect_req1`, `struct l4_kwq_connect_req2`, `struct l4_kwq_connect_req3`, `struct l4_kwq_offload_pg`, `struct l4_kwq_reset_req`, `struct l4_kwq_update_pg`, and `struct l4_kwq_upload`. These describe the multi-WQE TCP connection setup sequence, IPv6 extension data, keepalive and MSS settings, L2 page/offload information, and close/reset/upload completions.

The per-storm aggregative and non-aggregative contexts include `cstorm_iscsi_ag_context`, `tstorm_fcoe_ag_context`, `tstorm_tcp_tcp_ag_context_section`, `tstorm_iscsi_ag_context`, `ustorm_fcoe_ag_context`, `ustorm_iscsi_ag_context`, `xstorm_fcoe_ag_context`, `xstorm_tcp_tcp_ag_context_section`, `xstorm_iscsi_ag_context`, and `xstorm_l5cm_ag_context`. These represent firmware-maintained state for Cstorm/Tstorm/Ustorm/Xstorm engines: queue membership, producer/consumer values, timers, decision rules, TCP sequence variables, offload state flags, and completion rules.

The FCoE section defines Fibre Channel headers and payloads (`fcoe_fc_hdr`, `fcoe_fcp_rsp_payload`, `fcoe_fcp_cmd_payload`, `fcoe_fc_frame`), KWQE/KCQE forms (`fcoe_kcqe`, `fcoe_kwqe_header`, `fcoe_kwqe_init1/2/3`, `fcoe_kwqe_conn_offload1/2/3/4`, `fcoe_kwqe_conn_enable_disable`, `fcoe_kwqe_conn_destroy`, `fcoe_kwqe_destroy`, `fcoe_kwqe_stat`, `union fcoe_kwqe`), task context entries (`fcoe_task_ctx_entry`, `fcoe_tce_*`, `fcoe_sqe`, `fcoe_xfrqe`), storm contexts (`ustorm_fcoe_st_context`, `xstorm_fcoe_st_context`, `fcoe_context`), and ramrod parameter wrappers (`fcoe_init_ramrod_params`, `fcoe_stat_ramrod_params`, `fcoe_conn_offload_ramrod_params`, `fcoe_conn_enable_disable_ramrod_params`).

The iSCSI section defines CQ doorbell state, host queue BDs, PDU header overlays, task contexts, and full connection context. Important types include `iscsi_cq_db_prod_pnd_cmpltn_cnt`, `iscsi_cq_db_*`, `cstorm_iscsi_st_context`, `ustorm_iscsi_st_context`, `tstorm_iscsi_st_context`, `xstorm_iscsi_st_context`, `iscsi_context`, `union iscsi_pdu_headers_little_endian`, `iscsi_hq_bd`, `iscsi_l2_ooo_data`, and `iscsi_task_context_entry`. The PDU header structs model command, data-out, login, logout, task-management, text, and NOP-out headers in firmware-visible layout.

The L5 connection-manager section defines IPv6 and socket-address buffers, active/passive connection buffers, port listener attributes, passive connection search entries, slow-path elements, termination variables, and out-of-order enums: `ip_v6_addr`, `l5cm_conn_addr_params`, `l5cm_active_conn_buffer`, `l5cm_hash_input_string`, `l5cm_opaque_buf`, `l5cm_pcs_entry`, `l5cm_spe`, `l5cm_term_vars`, `tstorm_l5cm_tcp_flags`, `xstorm_l5cm_tcp_flags`, `enum tcp_ooo_event`, and `enum tcp_tstorm_ooo`.

## Control Flow and State
The file has no direct runtime control flow, but it defines several firmware-driven flows. A TCP offload connect is represented as a sequence of `l4_kwq_connect_req1`, optional IPv6 `l4_kwq_connect_req2`, and `l4_kwq_connect_req3`, followed by KCQ completions such as `L4_KCQE_OPCODE_VALUE_CONNECT_COMPLETE`. Close and abort flows use `l4_kwq_close_req` and `l4_kwq_reset_req`, with corresponding close/reset completion or remote close/reset indications.

FCoE control flow is modeled as ramrod batches: init is split across `fcoe_kwqe_init1/2/3`, connection offload across `fcoe_kwqe_conn_offload1/2/3/4`, then enable/disable, destroy, statistics, and function teardown use their own KWQE forms. Firmware completions are returned through `fcoe_kcqe`, with `FCOE_KCQE_RAMROD_COMPLETION`, layer-code, and linked-entry flags.

iSCSI control flow is stateful across Cstorm/Ustorm/Tstorm/Xstorm contexts. Host queues, request queues, R2T queues, completion queues, PDU header overlays, digest flags, task tables, and TCP sequence variables persist in DMA-visible context memory. Firmware consumes `iscsi_hq_bd` headers, updates producer/consumer and pending-completion fields, and uses task-context unions to track read/write, R2T, and retransmit state.

L5 connection-manager flow captures active connect parameters and passive SYN/final-ACK reduction. Passive connections use a hash input string, opaque listener data, SYN/ACK-specific segment unions, PCS attributes, and a receive segment buffer. Termination state is shared with iSCSI-style TCP termination variables.

## State and Persistence Behavior
The persistent state is external to the C translation unit: host DMA rings, firmware context memory, status/completion queues, doorbell records, page-block lists, and hardware timer blocks. Structures such as `fcoe_context` and `iscsi_context` aggregate per-storm state and are expected to be written to firmware-visible memory at exact offsets. Producer/consumer indices, queue toggle bits, sequence counters, digest flags, task IDs, VLAN fields, TCP timers, and connection IDs survive across individual function calls because firmware and driver both update them over time.

The file uses explicit little-endian annotations for many FCoE fields and conditional byte ordering for many mixed-width records. That means persistence includes byte layout, not just semantic values. A host must initialize reserved fields and masks correctly because firmware may interpret entire words, not only named C members.

## Dependencies and Integration Points
This header assumes kernel fixed-width types (`u8`, `u16`, `u32`, `__le16`, `__le32`) and shared HSI helpers such as `struct regpair`, `struct spe_hdr`, and `struct timers_block_context`, which are provided by adjacent Broadcom HSI headers in the bnx2x/CNIC include chain. It is tightly coupled to `cnic_if.h` through common KWQE/KCQE concepts and to CNIC implementation files that fill KWQE arrays, post ramrods, handle completions, and allocate context memory.

Integration points include the CNIC core driver, Broadcom bnx2/bnx2x Ethernet drivers exposing CNIC offload hooks, iSCSI upper-layer protocol code, FCoE offload code, firmware loading/HSI version compatibility, PCI DMA allocation, interrupt/KCQ delivery, status block handling, and management of context IDs (`cid`, `pg_cid`, `l5_cid`, FCoE connection IDs, and iSCSI connection IDs).

## Risks
The dominant risk is ABI drift. Reordering fields, changing integer types, removing duplicate endian branches, adjusting reserved fields, or renaming masks without checking generated firmware expectations can corrupt firmware-visible command/context layout. Endian risk is high because many structs are manually reordered rather than purely using `__le*` fields.

Other risks include mismatched opcode/status values, incorrect layer-code bits, wrong linked-WQE flags in multi-entry commands, stale FCoE/iSCSI HSI versions, uninitialized reserved fields leaking into firmware decision bits, producer/consumer wrap mistakes, task-ID/toggle-bit misuse, DMA address truncation through high/low fields, VLAN bitfield confusion, digest negotiation mismatches, and TCP offload state divergence between host and storm contexts.

Security and reliability risk is concentrated where firmware interprets network-originated storage protocol headers. The iSCSI PDU overlays and FCoE task contexts need strict validation by callers before they are handed to hardware; this header itself cannot enforce bounds, digest validity, task table limits, or queue occupancy.

## Test Signals
Useful build-time signals include compiling both little-endian and big-endian configurations where possible, sparse/endian checking, struct size/offset assertions against firmware HSI documentation or generated values, and allmodconfig coverage for CNIC, bnx2x, iSCSI, and FCoE combinations.

Runtime signals include successful CNIC registration, TCP offload connect/close/reset completions, iSCSI login and data I/O under digest and non-digest modes, FCoE init/offload/enable/stat/destroy ramrod completions, KCQ layer/opcode decoding, error-path completions for timeout/parity/NIC errors, out-of-order TCP handling, IPv6 connect setup, VLAN-tagged offload traffic, stress with queue wraparound, and reset/remove/reprobe without stale context or DMA state.
