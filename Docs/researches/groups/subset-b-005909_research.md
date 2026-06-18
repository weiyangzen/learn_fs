# Research: subset-b-005909

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/common_hsi.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/common_hsi.h

Purpose: defines QED's common host/firmware hardware-software interface: DMA address helpers, firmware version constants, per-block hardware limits, BAR/window offsets, doorbell formats, interrupt/status-block formats, parsing/error flags, function identifiers, timer contexts, DIF/DIX contexts, and shared small structures used by Ethernet, storage, RDMA, and LL2 headers.

Important APIs/types/functions: this header has no normal functions, but the macro and structure layout is the API. `PTR_LO`, `PTR_HI`, `DMA_LO_LE`, `DMA_HI_LE`, `DMA_REGPAIR_LE`, `HILO_64_REGPAIR`, and `HILO_DMA_REGPAIR` convert CPU and DMA addresses to/from QED `struct regpair` little-endian register pairs. Hardware constants cover ports/PFs/VFs/vports/L2 queues, QM queue counts, CAU/IGU/PXP memory windows, PBL/ILT sizing, DQ PWM offsets, global queue limits, and firmware version `8.59.1.0`. Shared types include `struct regpair`, `struct status_block`, `struct cau_pi_entry`, `struct cau_sb_entry`, `struct igu_prod_cons_update`, `struct core_db_data`, `struct db_l2_dpm_data`, `struct db_rdma_dpm_data`, `struct db_pwm_addr`, `struct parsing_and_err_flags`, `struct parsing_err_flags`, `struct pxp_ptt_entry`, `struct rdif_task_context`, `struct tdif_task_context`, and `struct timers_context`. Enums such as `protocol_type`, `db_dest`, `db_dpm_type`, `igu_int_cmd`, `l3_type`, `l4_protocol`, and `tunnel_next_protocol` give firmware-visible numeric values.

Control flow: QED client code and lower driver implementation populate these structures before ringing doorbells, initializing status blocks, mapping register windows, setting PXP pretend state, or passing task contexts to firmware. Doorbell flow is built from destination/aggregation fields plus producer values; interrupt flow writes `igu_prod_cons_update` commands and reads `status_block` producers; packet receive/classification flow decodes `parsing_and_err_flags`; storage offload flow carries DIF state through `rdif_task_context` and `tdif_task_context`.

State and persistence: the header itself stores no runtime state. It describes MMIO-visible, DMA-visible, and firmware-context state whose lifetime is owned by QED devices, queues, connections, and tasks. Many fields are little-endian snapshots persisted in host DMA memory until firmware consumes them; incorrect reuse or zeroing changes live hardware behavior, not only software bookkeeping.

Dependencies and integration points: depends on Linux integer, byteorder, bitops, slab, and DMA address types. It is included by `qed_chain.h`, `qed_if.h`, `eth_common.h` consumers, and protocol HSI headers. It bridges Linux driver code to Marvell/QLogic firmware, PCI BAR layout, IGU interrupt hardware, PXP register windows, queue manager hardware, and SCSI DIF-aware storage offloads.

Risks: the highest risk is ABI drift: bit masks, shifts, endianness, enum values, queue counts, or struct padding must match firmware exactly. Address helpers assume correct 64-bit split/merge and little-endian conversion. MMIO offsets and VF/PF BAR windows are hardware-specific. Doorbell and status-block fields have ordering implications; missing barriers or writing a wrong destination/aggregation selector can hang queues. DIF contexts are dense and easy to misconfigure, causing data-integrity failures rather than simple I/O errors.

Test signals: compile-test all QED protocol combinations and endianness-sensitive paths; boot on supported QED hardware or simulation; verify firmware version negotiation, PF/VF resource sizing, MSI-X/status-block interrupt delivery, doorbell producer updates, VF BAR access, LL2/RDMA/Ethernet queue bring-up, and DIF/DIX read/write validation. Regression tests should compare generated HSI layout offsets/sizes against firmware headers and exercise error CQEs, tunnel parsing flags, and PXP pretend paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/common_hsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/eth_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/eth_common.h

Purpose: defines the Ethernet-specific QED firmware interface for TX/RX rings, buffer descriptors, completion queue entries, tunneling parse metadata, RSS hash types, TPA/LRO aggregation CQEs, queue zones, and Ethernet doorbell payloads.

Important APIs/types/functions: constants define Ethernet HSI version `3.11`, BD page sizes, max BDs for normal and LSO packets, MTU/LSO payload limits, RX buffer thresholds, MAC/VLAN filter counts, RSS indirection/key sizes, TPA list sizes, multicast bin counts, and statistic counter sizing. TX layouts include `eth_tx_1st_bd_flags`, `eth_tx_data_1st_bd`, `eth_tx_data_2nd_bd`, `eth_tx_data_3rd_bd`, `eth_tx_data_4th_bd`, `eth_tx_1st_bd`, `eth_tx_2nd_bd`, `eth_tx_3rd_bd`, `eth_tx_4th_bd`, `eth_tx_bd`, and `union eth_tx_bd_types`. RX layouts include `eth_rx_bd`, `eth_fast_path_rx_reg_cqe`, TPA start/continue/end CQEs, `eth_slow_path_rx_cqe`, `union eth_rx_cqe`, and `eth_rx_pmd_cqe`. Enums cover destination port mode, address type, RX/TX tunnel type, TPA end reasons, pseudo-checksum mode, CQE type, and RSS hash type. `struct eth_db_data` is the L2 doorbell command.

Control flow: a client prepares TX BDs with packet address, byte count, checksum/LSO/VLAN/tunnel flags, then rings an Ethernet doorbell with a BD producer. Firmware writes RX CQEs into CQ rings, using regular CQEs for normal packets, TPA start/continue/end CQEs for aggregated packets, and slow-path CQEs for ramrod completions. Consumers decode parsing flags, RSS hash type, tunnel flags, VLAN tag, packet length, flow ID, PMD flags, and aggregation reason before recycling buffers. Queue zones expose RX producer state and interrupt coalescing parameters to storms.

State and persistence: ring state lives in DMA memory allocated by the QED client and in firmware queue contexts. The header defines transient descriptor/completion records rather than durable storage. Statistics counters and queue producers persist for the lifetime of queues/vports and must be reset intentionally during vport/queue lifecycle operations.

Dependencies and integration points: depends on common HSI types, especially `regpair`, `parsing_and_err_flags`, `coalescing_timeset`, and tunnel protocol enums. It is consumed by `qed_eth_if.h` and QED/qede datapath code, and integrates with Linux netdev features such as checksum offload, TSO/LSO, RSS, VLAN insertion/stripping, tunnels, XDP/PMD-style completion spacing, and LRO/TPA.

Risks: risks include BD count violations for LSO/tunnel packets, incorrect header offsets, stale or mismatched RSS/TPA state, endian mistakes in descriptor fields, failure to account for CQE gap padding, and tunnel checksum flags that do not match packet contents. TPA sequence errors can silently corrupt packet assembly if start/continue/end handling is wrong. Firmware-visible enum values must remain stable.

Test signals: run qede transmit/receive tests with checksum offload, VLAN insertion/removal, RSS, multicast/promiscuous filters, VXLAN/Geneve/GRE tunneling, TSO/LSO boundary sizes, TPA/LRO aggregation, RX buffer starvation, and slow-path CQE completions. Hardware counters and ethtool stats should reflect packet classes, drops, TPA aborts, and tunnel parsing. Layout tests should verify all BD/CQE sizes against firmware expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/eth_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/fcoe_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/fcoe_common.h

Purpose: defines the FCoE firmware interface for SCSI/FCP task contexts, protection information, FCP command/response/xfer payload containers, SQ/XferQ WQEs, connection offload ramrods, statistics, and FCoE doorbells.

Important APIs/types/functions: task data is split across `ystorm_fcoe_task_st_ctx`, `tstorm_fcoe_task_st_ctx`, `mstorm_fcoe_task_st_ctx`, per-storm aggregation contexts, and top-level `struct fcoe_task_context`. Data integrity and DIF/DIX state use `protection_info_ctx`, `fcoe_dix_desc_ctx`, `tdif_task_context`, and `rdif_task_context`. Payload and TX state use `fcoe_fcp_cmd_payload`, `fcoe_fcp_rsp_payload`, `fcoe_fcp_xfer_payload`, `fcoe_tx_data_params`, `fcoe_tx_mid_path_params`, and `union fcoe_tx_info_union_ctx`. Connection setup uses `fcoe_conn_offload_ramrod_data`, `fcoe_conn_terminate_ramrod_data`, `fcoe_init_func_ramrod_data`, and `fcoe_stat_ramrod_data`. WQE and request enums include `fcoe_sqe_request_type`, `fcoe_task_type`, `fcoe_mode_type`, `fcoe_device_type`, and `fcoe_completion_status`. `struct fcoe_wqe`, `struct fcoe_db_data`, `fcoe_rx_stat`, and `fcoe_tx_stat` are key queue/stat interfaces.

Control flow: the protocol driver initializes FCoE function resources, offloads a connection with queue PBL addresses, MAC addresses, FC IDs, VLAN and timer values, then posts SQ/XferQ elements representing FCP commands, data, XFER_RDY, responses, ABTS, cleanup, and sequence recovery. Firmware updates storm task contexts as data is transmitted/received, timers expire, DIF is checked, and completions are placed. Doorbells advance SQ producers, while termination ramrods point firmware to termination parameters.

State and persistence: FCoE exchange state is held in firmware task contexts and host task blocks for the lifetime of an exchange/task. Connection state is represented by offload ramrod parameters and firmware context. Statistics accumulate per PF for RX/TX packets, bytes, and silent drops. Nothing here persists across driver unload or firmware reset except what upper layers reconstruct from FC/FCoE login/session state.

Dependencies and integration points: depends on common QED types and storage-common SCSI structures such as `scsi_sge`, `scsi_sgl_params`, `scsi_cached_sges`, and `scsi_init_func_params`. Integrates QED firmware with FCoE upper-layer drivers, LL2/FIP handling, SCSI DIF/DIX, Fibre Channel sequence/exchange management, and MAC/VLAN fabric addressing.

Risks: dense task contexts have many firmware-owned fields; accidental host writes can break exchange state. FC timers, ABTS/sequence recovery flags, FC IDs, VLAN tags, and MAC address packing must match firmware and wire protocol. DIF/DIX flags and cached SGE handling can produce data-integrity errors. Queue PBL page and producer misconfiguration can strand exchanges or produce silent drops.

Test signals: exercise FCoE login, FIP discovery, FCP read/write, target and initiator modes, ABTS, sequence recovery, exchange cleanup, VLAN and non-VLAN traffic, DIF/DIX validation, error injection for CRC/task invalid/queue-full drops, and stats collection. Tests should inspect firmware completions and `qed_fcoe_stats` against expected RX/TX frame counts and drop reasons.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/fcoe_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/iscsi_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/iscsi_common.h

Purpose: defines the iSCSI/TCP offload firmware ABI: iSCSI constants/defaults, PDU header structures, DIF parameters, task contexts, connection offload/update/termination ramrods, CQE/UHQE/XHQE/SQ WQE formats, error codes, async event opcodes, statistics, and doorbell data.

Important APIs/types/functions: constants capture iSCSI defaults and limits for MTU, digests, InitialR2T, ImmediateData, PDU length, burst length, outstanding R2T, opcodes, login stages, and reserved ITT/TTT values. PDU structures include common, command, extended CDB, login/logout, data-in/out, R2T, NOP, text, TMF, response, reject, and async message headers, grouped in `union iscsi_task_hdr`. Task state uses `ystorm_iscsi_task_state`, `ystorm_iscsi_task_st_ctx`, per-storm aggregation contexts, `mstorm_iscsi_task_st_ctx`, `ustorm_iscsi_task_st_ctx`, and top-level `struct iscsi_task_context`. Connection command structures include `iscsi_conn_offload_params`, `iscsi_conn_update_ramrod_params`, `iscsi_spe_conn_offload`, `iscsi_spe_conn_offload_option2`, `iscsi_spe_conn_termination`, `iscsi_spe_conn_statistics`, `iscsi_spe_conn_mac_update`, and `iscsi_spe_func_init`. Completion/queue formats include `iscsi_cqe_*`, `union iscsi_cqe`, `iscsi_uhqe`, `iscsi_xhqe`, `iscsi_wqe`, and `iscsi_db_data`.

Control flow: function init configures rings, LL2 queue, debug flags, and SCSI queue parameters. Connection offload passes iSCSI queue PBLs plus TCP offload parameters to firmware; update ramrods enable digests, InitialR2T/ImmediateData, sequence sizing, and DIF modes after negotiation. Tasks are represented by WQEs and task contexts containing SGLs, PDU headers, sequence numbers, buffers, expected R2T/data SNs, and DIF flags. Firmware writes solicited/unsolicited CQEs and async EQEs for completions, task cleanup, protocol errors, TCP events, and connection errors. Doorbells update SQ producers.

State and persistence: per-connection TCP/iSCSI state and per-task SCSI/iSCSI state live in DMA task contexts and firmware contexts. CQE and queue elements are transient but drive upper-layer completion and error handling. Stats accumulate per storm/PF and per connection until reset. No durable session state is stored here; upper iSCSI layers must reconstruct after driver reset.

Dependencies and integration points: depends on QED common HSI, `tcp_common.h`, and `storage_common.h` structures for SCSI SGLs and TCP offload parameters. It integrates Linux iSCSI offload code with QED firmware, TCP state tracking, LL2 out-of-order queues, SCSI DIF, digest handling, and async connection events.

Risks: protocol correctness depends on exact iSCSI PDU layout and enum values. Digest flags, DIF-on-immediate, LUN mapper parameters, task IDs, ITT/TTT validation, and R2T sequence accounting are subtle. TCP option/offload mode mismatch can cause connection failure. Error enums are part of driver/firmware diagnosis; adding or renumbering them breaks event decoding. Ring threshold or BDQ misconfiguration can produce backpressure and drops.

Test signals: cover login negotiation, full-feature reads/writes, immediate data, R2T, unsolicited data, digests on/off, DIF-on-host and DIF-on-immediate, task cleanup, clear SQ, MAC update, connection termination, TCP abort/FIN/SYN async events, invalid opcode/ITT/TTT/error PDU paths, and stats reads/resets. Layout tests should verify all PDU header and task-context sizes/offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/iscsi_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/iwarp_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/iwarp_common.h

Purpose: provides small iWARP firmware constants shared by the QED RDMA implementation, mainly connection mode identifiers, shared queue page layout, WQE sizing limits, and maximum QP count.

Important APIs/types/functions: includes `rdma_common.h` and defines `IWARP_ACTIVE_MODE`, `IWARP_PASSIVE_MODE`, `IWARP_SHARED_QUEUE_PAGE_SIZE`, RQ/SQ PBL offsets and maximum sizes within that shared page, `IWARP_REQ_MAX_INLINE_DATA_SIZE`, `IWARP_REQ_MAX_SINGLE_SQ_WQE_SIZE`, and `IWARP_MAX_QPS`.

Control flow: RDMA/iWARP setup code uses these constants while allocating shared queue pages, laying out RQ/SQ PBL regions, sizing inline data/WQEs, and distinguishing active versus passive MPA connection setup.

State and persistence: no state is stored here. The constants constrain DMA memory layout and firmware resource allocation for iWARP queue pairs and requests.

Dependencies and integration points: depends on `linux/qed/rdma_common.h`. It is conceptually paired with `qed_rdma_if.h` iWARP connection-management operations and firmware RDMA context setup.

Risks: incorrect offsets or maximum sizes can overlap queue regions inside the shared page or allow WQEs firmware cannot parse. `IWARP_MAX_QPS` must match firmware/ILT resource assumptions.

Test signals: compile iWARP-enabled RDMA builds, create active and passive iWARP connections, test inline sends near 128 bytes, stress SQ/RQ PBL allocation, and verify maximum resource negotiation does not exceed firmware-supported QP limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/iwarp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/nvmetcp_common.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/nvmetcp_common.h

Purpose: defines QED's NVMe/TCP firmware ABI for function initialization, TCP/NVMe connection offload and update, SQ WQEs, CQEs, event opcodes, task contexts, CCCID-to-iTID mapping, and E5 storm aggregation contexts.

Important APIs/types/functions: init/offload structures include `nvmetcp_spe_func_init`, `nvmetcp_init_ramrod_params`, `nvmetcp_conn_offload_section`, `nvmetcp_conn_offload_params`, `nvmetcp_spe_conn_offload`, `nvmetcp_conn_update_ramrod_params`, and `nvmetcp_spe_conn_termination`. Command/event enums include `nvmetcp_ramrod_cmd_id`, `nvmetcp_eqe_opcode`, `nvmetcp_wqe_type`, `nvmetcp_task_type`, and `nvmetcp_fw_cqes_type`. Queue/completion formats include `nvmetcp_wqe`, `nvmetcp_db_data`, `nvmetcp_fw_cqe`, `nvmetcp_fw_cqe_data`, `nvmetcp_icresp_mdata`, and `nvmetcp_host_cccid_itid_entry`. Task context structures include `ystorm_nvmetcp_task_state`, `nvmetcp_task_hdr_aligned`, `mstorm_nvmetcp_task_st_ctx`, `ustorm_nvmetcp_task_st_ctx`, E5 per-storm aggregation contexts, and top-level `e5_nvmetcp_task_context`.

Control flow: function init configures queue ring page counts, LL2 out-of-order queue, counters, TCP init parameters, and SCSI-style function queue settings. Connection offload supplies SQ/R2TQ/XHQ/UHQ PBLs, TCP option-2 offload parameters, physical queues, default CQ, initial ACK, and a CCCID-to-iTID table. Connection update enables header/data digest and PDU size limits. WQEs describe normal I/O, cleanup, middle path, and ICReq exchange work; firmware emits CQEs for normal completions, cleanup, dummy entries, IC response metadata, and connection errors. Doorbells update SQ producer state.

State and persistence: per-task state lives in firmware-visible host task contexts; per-connection TCP/NVMe state is held in firmware and keyed by connection IDs, ICIDs, CCCIDs, and iTIDs. The CCCID mapping table is host DMA memory that must remain valid while the connection is offloaded. No durable NVMe session state is persisted here.

Dependencies and integration points: depends on `tcp_common.h`, Linux `<linux/nvme-tcp.h>`, common QED register pairs, and storage SGL helpers. It backs the public `qed_nvmetcp_if.h` APIs and integrates QED firmware with NVMe/TCP host controller logic, TCP offload, digest validation, LL2 filtering, and storage SGL/DIF-like metadata.

Risks: the header is newer and has placeholder/reserved fields, so firmware/driver version drift is a risk. CCCID/iTID table sizing and lifetime are critical. Digest update flags, NVMe/TCP mode bits, ICReq/ICResp metadata, and opaque task handles must align with the Linux NVMe/TCP PDU definitions. Errors in context padding or reserved E5 contexts can corrupt firmware parsing.

Test signals: test NVMe/TCP connect/offload/update/destroy, ICReq exchange, read/write I/O, cleanup, digest on/off, source/destination TCP port filters, CCCID mapping range checks, async TCP error events, and CQE decoding. Layout checks should compare task context, WQE, and CQE sizes to firmware-generated expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/nvmetcp_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_chain.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_chain.h

Purpose: implements QED's generic DMA ring/chain abstraction used for producer/consumer queues, including single-page, next-pointer linked-page, and PBL-backed modes with 16-bit or 32-bit producer/consumer counters.

Important APIs/types/functions: `enum qed_chain_mode`, `qed_chain_use_mode`, and `qed_chain_cnt_type` define layout and counter semantics. `struct qed_chain` stores fast-path element pointers, PBL address table, counter union, capacity, page/element sizing, mode, slow-path allocation metadata, and optional external PBL state. `struct qed_chain_init_params` describes allocation input. Macros calculate elements per page, unusable next-pointer slots, usable elements, and page count. Inline APIs include producer/consumer index getters, used/left calculations, `qed_chain_advance_page`, `qed_chain_return_produced`, `qed_chain_produce`, `qed_chain_get_capacity`, `qed_chain_recycle_consumed`, `qed_chain_consume`, `qed_chain_reset`, `qed_chain_get_last_elem`, `qed_chain_set_prod`, and `qed_chain_pbl_zero_mem`.

Control flow: queue allocation fills a `qed_chain` with pages and optional PBL metadata. Producers call `qed_chain_produce()` to get the next writable element and later ring a doorbell; consumers call `qed_chain_consume()` for firmware-produced elements. In consume-mode chains, reset pre-produces empty elements by recycling consumed entries. When an index reaches the last usable slot on a page, `qed_chain_advance_page()` wraps via linked `qed_chain_next`, resets to the single page base, or advances through the PBL address table.

State and persistence: chain state is in-memory driver state plus DMA pages visible to firmware. Producer/consumer indices and page indices persist for the queue lifetime and are mutated on every enqueue/dequeue. PBL tables and chain pages must remain DMA-mapped until queue teardown.

Dependencies and integration points: depends on Linux types/list/sizes/slab, byteorder, and `common_hsi.h` `regpair`. Allocation/free are exposed through `qed_common_ops.chain_alloc` and `chain_free` in `qed_if.h`; chains back Ethernet BDs/CQEs, storage queues, LL2 queues, SPQ-style single chains, and RDMA rings.

Risks: off-by-one errors around unusable next-pointer slots, non-power-of-two element counts, page wrapping, 16-bit counter overflow, and `qed_chain_set_prod()` page-index rewind can corrupt queue state. Callers must check `qed_chain_get_elem_left()` before producing; the helpers do not enforce capacity. PBL mode assumes address table validity and stable DMA mappings.

Test signals: unit-test page-count/usable-element macros, produce/consume across page boundaries for all modes, U16/U32 wraparound, reset behavior for all intended-use modes, `qed_chain_set_prod()` rewind/advance in PBL mode, and zeroing PBL memory. Hardware tests should stress RX/TX rings with small page counts and maximum BD occupancy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_chain.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_eth_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_eth_if.h

Purpose: declares the public Ethernet client interface exported by the QED core to qede/netdev code, including device info, vport lifecycle, queue start/stop, filters, RSS, tunnel configuration, PTP, DCB, SR-IOV access, stats, and callbacks.

Important APIs/types/functions: queue structures include `qed_queue_start_common_params`, `qed_rxq_start_ret_params`, and `qed_txq_start_ret_params`. Device/vport/filter structures include `qed_dev_eth_info`, `qed_start_vport_params`, `qed_update_vport_params`, `qed_update_vport_rss_params`, `qed_filter_ucast_params`, `qed_filter_mcast_params`, `qed_tunn_params`, and `qed_ntuple_filter_params`. Enums cover filter config mode, RX mode, xcast operation type, filter type, and PTP filter/tx timestamp types. Callback/ops tables include `qed_eth_cb_ops`, optional `qed_eth_dcbnl_ops`, `qed_eth_ptp_ops`, and the top-level `qed_eth_ops`. Entry points are `qed_get_eth_ops()` and `qed_put_eth_ops()`.

Control flow: an Ethernet client gets ops, probes/common-starts the device, fills device info, registers callbacks, starts vports, starts RX/TX queues with status-block indices and PBL addresses, configures RSS/filters/tunnels/PTP/DCB as needed, handles slow-path RX CQE completions, gathers stats, then stops queues/vports and releases ops. Callback flow notifies the client about forced MACs, tunnel-port updates, link/DCBX/common events, and recovery.

State and persistence: this header defines contracts for runtime QED Ethernet state: vports, queues, RSS tables/keys, MAC/VLAN/multicast filters, ntuple/aRFS filters, tunnel ports, PTP timestamping, and stats. State persists in firmware until explicitly updated/stopped or reset; the header itself stores no state.

Dependencies and integration points: includes Linux list and if_link/DCB types, `eth_common.h`, `qed_if.h`, and `qed_iov_if.h`. Integrates QED with Linux netdev/qede, ethtool/DCB, PTP hardware timestamping, SR-IOV VF management, XDP capability reporting, tunnel offload configuration, and aRFS/searcher filters.

Risks: mismatched queue IDs/status-block indices, wrong PBL sizes, stale RSS pointer arrays, filter add/delete semantics, and VF-relative identifiers can misroute traffic. Optional DCB/SR-IOV function pointers depend on configs. PTP drift limit and timestamp filter selections need device support. aRFS header DMA buffers must be valid long enough for firmware consumption.

Test signals: qede open/close, MTU changes, RX/TX queue scaling, RSS indirection/key updates, VLAN/MAC/multicast/promiscuous filters, ntuple/aRFS add/remove/drop, tunnel port updates, PTP timestamp read/adjust/enable/disable, DCB operations under `CONFIG_DCB`, SR-IOV VF configuration, and stats consistency through ethtool.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_eth_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_fcoe_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_fcoe_if.h

Purpose: declares the public QED FCoE client interface used by FCoE upper layers to start firmware resources, acquire/offload/destroy FCoE connections, access LL2, and collect FCoE stats.

Important APIs/types/functions: `qed_fcoe_stats` mirrors RX/TX FCoE counters and silent-drop reasons. `qed_dev_fcoe_info` returns common device info, primary/secondary BDQ request queue addresses, WWPN/WWNN, and CQ count. `qed_fcoe_params_offload` carries SQ page addresses, MACs, FC payload/timer values, VLAN tag, FC source/destination IDs, flags, and default queue. `qed_fcoe_tid` describes firmware task blocks. `qed_fcoe_cb_ops` extends common callbacks with `get_login_failures`. `qed_fcoe_ops` exposes `fill_dev_info`, `register_ops`, `ll2`, `start`, `stop`, `acquire_conn`, `release_conn`, `offload_conn`, `destroy_conn`, and `get_stats`; `qed_get_fcoe_ops()`/`qed_put_fcoe_ops()` manage ops access.

Control flow: a client obtains FCoE ops, registers callbacks, reads device info, starts FCoE with a task-block descriptor, optionally uses LL2 for FIP/control traffic, acquires a firmware connection handle/doorbell, offloads connection parameters, posts protocol work through its rings, destroys the connection with termination parameters, releases the handle, and stops FCoE.

State and persistence: connection handles, firmware CIDs, doorbell addresses, task blocks, and BDQ/CQ resources persist while FCoE is started and each connection is active. Stats persist until reset or restart. FC login/session durability is handled by upper layers, not by this header.

Dependencies and integration points: includes `qed_if.h` and uses `fc_addr_nw` from FCoE common definitions through transitive include expectations. Integrates QED core with FCoE storage drivers, LL2 packet path, firmware task memory, Fibre Channel identifiers, and management firmware TLV reporting.

Risks: caller-owned task blocks and PBL addresses must remain DMA-valid. Incorrect WWN/FC ID/MAC/VLAN/timer values prevent fabric login or data exchange. The ops table assumes `ll2` is available and configured for control traffic. `destroy_conn` termination DMA address lifetime is a common failure point.

Test signals: FCoE start/stop, task block sizing, FIP login, connection acquire/offload/release, FC read/write, ABTS/termination, LL2 control packet send/receive, login failure reporting, stats counters for RX/TX and silent-drop reasons, and module get/put lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_fcoe_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_if.h

Purpose: defines the common QED client-driver interface shared by Ethernet, FCoE, iSCSI, NVMe/TCP, and RDMA: device probing, slowpath lifecycle, PF resource parameters, interrupts/status blocks, link/NVM/devlink/recovery operations, debug macros, statistics structures, DCBX/LLDP data, management firmware TLVs, and field-manipulation helpers.

Important APIs/types/functions: resource parameter types include `qed_eth_pf_params`, `qed_fcoe_pf_params`, `qed_iscsi_pf_params`, `qed_nvmetcp_pf_params`, `qed_rdma_pf_params`, and `qed_pf_params`. Device/lifecycle types include `qed_dev`, `qed_dev_info`, `qed_probe_params`, `qed_slowpath_params`, `qed_int_info`, `qed_sb_info`, `qed_link_params`, `qed_link_output`, `qed_common_cb_ops`, `qed_selftest_ops`, and `qed_common_ops`. DCBX/LLDP and MFW TLV structures cover application priorities, ETS/PFC, local/remote LLDP, Ethernet/FCoE/iSCSI telemetry, and time fields. Helpers include `DIRECT_REG_WR/RD/WR64`, `SET_FIELD`, `GET_FIELD`, `GET_MFW_FIELD`, `SET_MFW_FIELD`, `DB_ADDR_SHIFT`, debug print macros, `qed_sb_update_sb_idx`, `qed_sb_ack`, and `internal_ram_wr`.

Control flow: protocol clients probe a PCI function with `qed_common_ops.probe`, set names and PF params, start slowpath, allocate interrupts/status blocks/chains, configure link/NVM/devlink as needed, run protocol-specific ops, handle callbacks for link/DCBX/recovery/errors, and stop/remove on teardown. Status-block flow reads the producer from DMA memory and writes an IGU ack MMIO command. Recovery and doorbell recovery APIs let clients register doorbells, report fatal errors, and trigger/prolog recovery.

State and persistence: QED common state includes PCI resources, firmware/MFW versions, interrupt vectors, status-block acknowledgments, PF resource allocations, link config/output, NVM images/config, devlink health reporters, debug level/module settings, and stats. Persistent data can be written to NVM through common ops; most other state is runtime hardware/firmware state.

Dependencies and integration points: includes Linux ethtool, interrupt, netdevice, PCI, skbuff, io, devlink, and QED common/chain headers. It is the central contract between QED core and all protocol-specific client modules, Linux devlink health, ethtool link modes, DCBX, PCI power management, NVM flashing, module EEPROM access, and management firmware reporting.

Risks: this header is broad and ABI-adjacent. PF params must be set before slowpath start or resources/ILT sizing can be wrong. Status-block ack writes need correct ordering and IGU address. Field macros can silently truncate if masks/shifts are wrong. NVM flashing/config reads are persistent and high-risk. Callback lifetimes, devlink registration order, and recovery/doorbell recovery state must be synchronized with device removal.

Test signals: probe/remove, slowpath start/stop, MSI-X allocation, status-block interrupt ack, chain allocation/free, link set/get across advertised/forced/FEC/EEE modes, NVM image read/flash failure handling, module EEPROM read, devlink health reporting, recovery paths, doorbell recovery add/delete/replay, DCBX AEN callbacks, debug-level filtering, and stats reads on both BB/AH device types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_iov_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_iov_if.h

Purpose: declares the SR-IOV hypervisor-facing operation table that lets a PF driver configure and manage child VFs.

Important APIs/types/functions: `struct qed_iov_hv_ops` contains callbacks for `configure`, `set_mac`, `set_vlan`, `get_config`, `set_link_state`, `set_spoof`, `set_rate`, and `set_trust`. It includes `qed_if.h` for `struct qed_dev` and Linux VF info types via that dependency.

Control flow: when SR-IOV is enabled, the Ethernet ops table can expose `qed_iov_hv_ops` to the PF-side netdev. Administrative operations from iproute2/sysfs/netdev call these callbacks to create VFs, assign MAC/VLAN, query VF config, force link state, enable/disable spoof checking, set min/max rates, and mark VFs trusted.

State and persistence: VF configuration is runtime PF/firmware state and may be reflected in hardware bulletin/config structures. It is not stored by this header. Some settings may survive until PF reset or VF teardown depending on core implementation.

Dependencies and integration points: integrates QED Ethernet SR-IOV support with Linux netdev VF administration (`ifla_vf_info`) and the optional `CONFIG_QED_SRIOV` pointer in `qed_eth_ops`.

Risks: incorrect VF IDs, trust/spoof settings, or rate limits can compromise isolation or traffic shaping. MAC/VLAN operations must coordinate with VF driver state and firmware bulletin updates. Optional availability depends on SR-IOV config.

Test signals: create/destroy VFs, set/query VF MAC and VLAN, force link up/down/auto, spoof-check toggles, min/max rate limits, trust mode, VF reset while PF settings change, and negative tests for out-of-range VF IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_iov_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_iscsi_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_iscsi_if.h

Purpose: declares the public QED iSCSI offload client interface for device discovery, firmware start/stop, connection acquire/offload/update/destroy, SQ clearing, MAC change, async events, LL2 access, and stats collection.

Important APIs/types/functions: `iscsi_event_cb_t` is the async event callback signature. `qed_iscsi_stats` exposes RX/TX packet, byte, R2T/data PDU, threshold, retransmit, and dropped-task counters. `qed_dev_iscsi_info` reports common info, BDQ request queue addresses, and CQ count. `qed_iscsi_id_params` describes MAC/IP/port endpoints. `qed_iscsi_params_offload` carries layer code, SQ PBL, initial TCP ACK, source/destination endpoints, VLAN, TCP/IP state variables, timers, window scaling, MSS, TTL/TOS, and retransmit/keepalive state. `qed_iscsi_params_update` carries negotiated digest and iSCSI sequence/PDU sizing flags. `qed_iscsi_tid` describes task memory blocks. `qed_iscsi_ops` exposes the lifecycle and connection operations; `qed_get_iscsi_ops()`/`qed_put_iscsi_ops()` manage ops access.

Control flow: a client starts iSCSI with task blocks plus async event context/callback, acquires a connection handle and firmware CID/doorbell, offloads TCP+iSCSI state, updates negotiated iSCSI parameters after login, posts SQ work through firmware-defined rings, handles async connection events, clears SQ or changes MAC when needed, destroys the connection, releases it, reads stats, and stops iSCSI.

State and persistence: active connection state is split between client-owned connection objects, firmware contexts, doorbell addresses, task blocks, and TCP/iSCSI sequence variables. Update flags persist in firmware until another update or teardown. Statistics are runtime counters. No session state is durable across reset without upper-layer recovery.

Dependencies and integration points: includes `qed_if.h` and exposes an LL2 ops pointer for supporting packet paths. It is backed by `iscsi_common.h` ramrods and integrates with Linux iSCSI offload transport, TCP offload state, LL2 out-of-order handling, and management firmware telemetry.

Risks: offload requires a coherent snapshot of TCP sequence/window/timer state; stale or partially initialized fields can break the connection. Digest and InitialR2T/ImmediateData update flags must match negotiated login settings. Async event callback lifetime must exceed firmware event delivery. `destroy_conn` and `clear_sq` ordering can race with completions.

Test signals: login/offload/update, reads/writes with and without header/data digest, immediate data/R2T negotiation, async abort/close/timeout events, SQ clear, MAC change, connection teardown with abort flag, stats reads, recovery during active I/O, and invalid endpoint/IP-version inputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_iscsi_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_ll2_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_ll2_if.h

Purpose: declares QED's Light L2 interface, a low-level packet path used by storage and RDMA clients for control, out-of-order, test, FCoE, TCP ULP, RoCE, and iWARP traffic outside the main Ethernet netdev queues.

Important APIs/types/functions: enums classify LL2 connection type, RX connection type, RoCE flavor, TX destination, and error handling. `qed_ll2_stats` reports invalid GSI headers, packet length/type/checksum errors, drops, and RX/TX byte/packet counters. Callback data and types include `qed_ll2_comp_rx_data`, RX/TX complete and release callbacks, slowpath callback, and `qed_ll2_cbs`. Connection setup uses `qed_ll2_acquire_data_inputs` and `qed_ll2_acquire_data`; TX uses `qed_ll2_tx_pkt_info`. Simpler netdev-style ops use `qed_ll2_cb_ops` and `qed_ll2_params`. `qed_ll2_ops` exposes `start`, `stop`, `start_xmit`, `register_cb_ops`, and `get_stats`. `qed_ll2_alloc_if`/`qed_ll2_dealloc_if` are real only under `CONFIG_QED_LL2`, otherwise stubs.

Control flow: a client registers packet callbacks, starts LL2 with MTU/drop/VLAN/MAC parameters, optionally acquires lower-level LL2 connections with descriptors and callbacks, posts RX buffers, prepares TX packets and fragments, receives completion/release callbacks, handles slowpath notifications, and stops/deallocates the interface. TX destination can send to network, loopback, or drop.

State and persistence: LL2 connection handles, descriptor rings, RX buffers, TX fragments, callbacks, and stats are runtime state owned by QED core and clients. Buffer cookies and DMA addresses must remain valid until release/completion callbacks return ownership.

Dependencies and integration points: includes Linux netdevice/skbuff/PCI/interrupt headers and `qed_if.h`. It integrates with FCoE FIP/control traffic, iSCSI out-of-order/TCP ULP traffic, RoCE/iWARP RDMA CM/control packets, and optional GSI handling.

Risks: callback lifetime and buffer ownership are central risks. Misconfigured MTU, descriptor counts, `tx_max_bds_per_packet`, or error handling can drop control traffic. Non-LL2 builds expose null ops except allocation stubs, so callers must respect config availability. Fragment mapping and `frags_mapped` semantics must match DMA ownership.

Test signals: build with and without `CONFIG_QED_LL2`, start/stop LL2, send SKBs with FIP discovery flag, acquire/establish/terminate/release low-level connections via RDMA ops, post RX buffers, verify RX/TX complete and release callbacks, exercise network/loopback/drop destinations, inject packet-too-big/no-buffer errors, and validate LL2 stats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_ll2_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_nvmetcp_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_nvmetcp_if.h

Purpose: declares the public QED NVMe/TCP offload interface for starting firmware resources, offloading/updating TCP/NVMe connections, configuring TCP port filters, initializing I/O task contexts, and handling async events.

Important APIs/types/functions: constants define max I/O size and NVMe/TCP header sizes using Linux NVMe/TCP PDU structures. `nvmetcp_event_cb_t` is the async event callback. `qed_dev_nvmetcp_info`, `qed_nvmetcp_tid`, and `qed_nvmetcp_id_params` describe device, task blocks, and endpoints. `qed_nvmetcp_params_offload` carries SQ PBL, CCCID-to-iTID table address/range, default CQ, endpoint identities, TCP keepalive/timer/congestion/window/MSS/VLAN/TOS settings, and feature booleans. `qed_nvmetcp_params_update` carries max I/O/PDU lengths plus digest enablement. `nvmetcp_sge`, `storage_sgl_task_params`, and `nvmetcp_task_params` are used by I/O initialization helpers. `qed_nvmetcp_ops` exposes common/LL2 ops, lifecycle/connection operations, source/destination TCP port filters, `clear_all_filters`, `init_read_io`, `init_write_io`, `init_icreq_exchange`, and `init_task_cleanup`. Entry points are `qed_get_nvmetcp_ops()` and `qed_put_nvmetcp_ops()`.

Control flow: the NVMe/TCP client starts firmware with task blocks and an async event callback, adds TCP port filters, acquires/offloads a connection with endpoint/TCP state and CCCID mapping, updates negotiated PDU/digest limits, calls task-init helpers to fill firmware WQEs/contexts for read, write, ICReq, or cleanup, rings queue doorbells through the returned doorbell path, handles completions/events, destroys/releases the connection, clears filters, and stops the protocol.

State and persistence: active state includes task blocks, SGLs, opaque task context pointers, CCCID mapping table, firmware connection ID/handle, port filters, digest/PDU limits, and async callback context. These are runtime and must be rebuilt after reset. SGL and task context memory must remain valid until firmware completion.

Dependencies and integration points: includes `qed_if.h`, `storage_common.h`, `nvmetcp_common.h`, and Linux NVMe/TCP definitions. It integrates QED firmware with the Linux NVMe/TCP host path, TCP offload state, storage SGL handling, LL2 filtering/control, and async event delivery.

Risks: task-init helpers write firmware contexts through caller-provided pointers, so uninitialized `task_params`, wrong SGL counts, or invalid physical addresses cause firmware-visible corruption. Digest/PDU settings must match NVMe/TCP negotiation. Port filters can affect traffic steering for multiple connections. CCCID range and table lifetime are critical for completion mapping.

Test signals: connection start/offload/update/destroy, source/destination port filter add/remove/clear, ICReq exchange, read and write I/O task initialization, cleanup initialization, digest enabled/disabled I/O, max I/O boundary at `0x800000`, async TCP/NVMe error events, and SGL edge cases including small middle SGE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_nvmetcp_if.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_rdma_if.h -->
# sources/distributed-fs/ceph-client/include/linux/qed/qed_rdma_if.h

Purpose: declares the public QED RDMA interface for RoCE and iWARP: device/port capabilities, RDMA start parameters, PD/XRCD/CQ/QP/SRQ/TID lifecycle, RoCE addressing and congestion control, LL2 packet operations, iWARP connection management, stats/counters, and event callbacks.

Important APIs/types/functions: capability and state types include `qed_roce_qp_state`, `qed_rdma_qp_type`, `qed_rdma_tid_type`, `qed_rdma_events`, `qed_rdma_device`, `qed_rdma_port`, `qed_roce_capability`, `qed_rdma_type`, and `qed_dev_rdma_info`. Setup types include `qed_rdma_cnq_params`, `qed_rdma_cq_mode`, `qed_roce_dcqcn_params`, `qed_rdma_start_in_params`, and `qed_rdma_add_user_out_params`. Resource types cover TID registration, CQ/SRQ/QP create/modify/query/destroy, stats, counters, GIDs, and RoCE mode. iWARP CM uses `qed_iwarp_cm_info`, event params, connect/listen/accept/reject/RTR structs, and `iwarp_event_handler`. `qed_roce_ll2_packet` describes RoCE LL2 packets. `qed_rdma_ops` is the central operations table; `qed_get_rdma_ops()` returns it.

Control flow: an RDMA client initializes QED RDMA with CNQ PBLs, event callbacks, CQ mode, DCQCN params, MTU/MAC, and iWARP flags. It adds users/DPIs, allocates PDs/XRCDs/TIDs, creates CQs/SRQs/QPs, transitions QPs through modify calls, registers/deregisters memory, updates CNQ producers, posts LL2 packets/buffers for RoCE/iWARP control traffic, handles affiliated/unaffiliated events, and tears resources down. For iWARP, it creates listeners or active connects, then accepts/rejects/finishes MPA/RTR flows through endpoint contexts.

State and persistence: RDMA state includes firmware RDMA context, CNQ pages, DPIs/user doorbell mappings, PD/XRCD/CQ/QP/SRQ/TID allocations, registered memory keys/PBLs, QP state and PSNs, GID/PKEY tables, DCQCN settings, LL2 connection handles, and iWARP endpoint/listen contexts. State is runtime and is invalidated by RDMA stop/device reset.

Dependencies and integration points: includes `qed_if.h`, `qed_ll2_if.h`, and `rdma_common.h`; uses Linux list/slab/delay/types. It integrates QED with Linux RDMA core providers, RoCE v1/v2 addressing, iWARP MPA/TCP connection management, LL2 packet transmission, MSI-X/CNQ interrupts, memory registration, and congestion control.

Risks: resource lifetimes are complex: QPs must not outlive CQs/PDs/MRs, TID registration must match PBL/page sizes and access flags, and user DPI mappings must be removed safely. QP modify masks control which fields are valid; missing mask bits or wrong RoCE mode/GID/MAC/VLAN/PSN values cause connectivity failures. iWARP endpoint callback contexts and private data lifetimes are sensitive. LL2 packet segmentation must fit `RDMA_MAX_SGE_PER_SQ_WQE`.

Test signals: RDMA device/port query, start/stop, interrupt allocation/CNQ producer updates, PD/XRCD allocation, CQ/SRQ/QP create/modify/query/destroy, MR/TID register/deregister for normal and DMA MRs, RoCE v1/v2 IPv4/IPv6 traffic, DCQCN enablement, LL2 control packet TX/RX, iWARP active/passive connect/listen/accept/reject/RTR/disconnect/error events, stats/counter reads, and teardown under outstanding events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/qed/qed_rdma_if.h -->
