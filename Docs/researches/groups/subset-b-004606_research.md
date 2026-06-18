# subset-b-004606 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mng_tlv.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mng_tlv.c

Purpose: Handles management-firmware driver TLV requests. It reads a TLV request stream from MCP public shared memory, determines which protocol groups are requested, asks the driver/MFW integration layer to populate generic/Ethernet/FCoE/iSCSI data, patches available values into the TLV buffer, writes the converted buffer back, and sends `DRV_MSG_CODE_GET_TLV_DONE`.

Important APIs/types/functions: `struct qed_tlv_parsed_buf` provides a pointer plus scratch storage for TLV values. `qed_mfw_get_tlv_group()` maps `DRV_TLV_*` IDs into `QED_MFW_TLV_GENERIC`, `ETH`, `FCOE`, or `ISCSI`. Group-specific getters (`qed_mfw_get_gen_tlv_value()`, `qed_mfw_get_eth_tlv_value()`, `qed_mfw_get_fcoe_tlv_value()`, `qed_mfw_get_iscsi_tlv_value()`) return a byte length and value pointer only when the matching `*_set` flag is present. `qed_mfw_get_tlv_time_value()` sanitizes time fields and formats fixed-size timestamp TLVs. `qed_mfw_update_tlvs()` walks a TLV buffer for one group and copies changed values. `qed_mfw_process_tlv_req()` is the external entry point.

Control flow: The entry point reads `public_global.data_ptr` and `data_size`, allocates a `vzalloc()` buffer, converts each MCP-read dword from the big-endian return format back into the little-endian TLV stream, and makes one header pass to OR together requested TLV groups. It masks groups that are incompatible with the current personality, then calls `qed_mfw_update_tlvs()` once per surviving group. The update pass allocates `union qed_mfw_tlv_data`, fills it through `qed_mfw_fill_tlv_data()`, walks TLV records using `sizeof(struct qed_drv_tlv_hdr) + 4 * tlv_length`, chooses the correct getter, sets `QED_DRV_TLV_FLAGS_CHANGED`, clamps length to the firmware-declared value area, and copies data after the header. Finally the driver writes each dword back with CPU-to-big-endian conversion and notifies MCP even on most local failures.

State and persistence: No long-lived driver state is owned here. Persistence is the MCP shared-memory TLV buffer and the management-firmware completion mailbox. The temporary TLV-data union and request buffer are freed before return.

Dependencies/integration: Depends on TLV ID/layout definitions from MCP headers, `qed_mfw_fill_tlv_data()` for live driver counters/settings, `qed_rd()`/`qed_wr()` for shared memory access, personality helpers such as `QED_IS_L2_PERSONALITY()`, and `qed_mcp_cmd()` for completion.

Risks: The parser trusts firmware-provided `data_size` and per-record `tlv_length`; malformed lengths could desynchronize the offset walk. Several FCoE TLV families compute array indices from sparse TLV IDs, so enum drift can produce wrong indexing. Time formatting uses a compact 14-byte scratch buffer and non-padded decimal fields. Error handling still sends GET_TLV_DONE, so consumers must inspect whether changed flags were set rather than assuming all requested data was filled.

Test signals: Exercise empty size, unknown TLV IDs, each personality mask, unavailable `*_set` fields, oversize value clamping, endian round trips, and representative generic/Ethernet/FCoE/iSCSI TLVs. Fault-inject `vzalloc()` and `qed_mfw_fill_tlv_data()` failures and confirm MCP completion is still issued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_mng_tlv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.c

Purpose: Implements the QED core-facing NVMe/TCP offload API. It starts/stops the firmware TCP ULP function, manages offloaded connection handles and chains, translates upper-layer connection parameters into firmware ramrods, exposes LL2/filter helpers, and exports `qed_get_nvmetcp_ops()`.

Important APIs/types/functions: Function lifecycle is driven by `qed_sp_nvmetcp_func_start()` and `qed_sp_nvmetcp_func_stop()`. Connection ramrods are `qed_sp_nvmetcp_conn_offload()`, `qed_sp_nvmetcp_conn_update()`, `qed_sp_nvmetcp_conn_terminate()`, and `qed_sp_nvmetcp_conn_clear_sq()`. Resource helpers allocate/reuse `struct qed_nvmetcp_conn`, acquire/release TCP ULP CIDs, allocate R2TQ/UHQ/XHQ chains, and hash active handles in `cdev->connections`. Public ops include `start`, `stop`, `acquire_conn`, `release_conn`, `offload_conn`, `update_conn`, `destroy_conn`, `clear_sq`, LLH TCP-port filters, and task initialization callbacks from `qed_nvmetcp_fw_funcs.c`.

Control flow: `qed_nvmetcp_start()` posts an init-function ramrod, registers an async callback, sets `QED_FLAG_STORAGE_STARTED`, initializes the connection hash, and optionally returns TID block geometry. `acquire_conn` allocates a hash wrapper, acquires a protocol CID, reuses or allocates connection queue chains, calculates firmware CID/doorbell, and inserts the connection into the hash. `offload_conn` copies MAC/IP/TCP/NVMe/TCP settings into the connection object and posts an offload ramrod with PQs, PBL addresses, CCCID/ITID table, and TCP parameters. Update and terminate paths look up the handle and post narrower ramrods. Stop refuses to run while active handles remain, posts destroy-function, unregisters the async callback, and clears the storage-started flag.

State and persistence: Per-hwfn state lives in `p_hwfn->p_nvmetcp_info`, including a spinlock, free-list cache of connection objects, event callback, and event context. Active connection ownership is represented by `cdev->connections`; cached inactive connections remain on the free list until `qed_nvmetcp_free()`, which frees chains and the info object. Firmware-visible state includes CIDs, queue PBLs, doorbells, function init settings, and connection ramrods.

Dependencies/integration: Integrates with the SPQ/ramrod layer, context manager CID/TID APIs, QED chain allocator, LL2 queues, CM PQ selection, LLH TCP filters, MCP/device info, and the exported `linux/qed/qed_nvmetcp_if.h` protocol interface.

Risks: Stop requires all handles to be released; a missed release blocks function shutdown. Connection hash operations are not protected by the NVMe/TCP spinlock, so callers must respect higher-level serialization. `qed_nvmetcp_acquire_connection()` releases the CID on chain allocation failure, but reusable objects are returned to the free list and must not retain stale per-connection fields that affect later offloads. Async callback absence returns `-EINVAL` after logging. Update uses iSCSI-named flag fields for NVMe/TCP, which makes firmware contract drift easy to miss.

Test signals: Cover start/stop idempotency, start failure cleanup after TID-info allocation, acquire/release/free-list reuse, offload with IPv4 and IPv6, digest/ECN/keepalive/timestamp flags, destroy/clear/update invalid handles, stop with outstanding connections, async event callback delivery, and fault injection for CID and chain allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.h

Purpose: Defines internal NVMe/TCP offload state used by `qed_nvmetcp.c` and provides config-gated allocation/setup/free declarations.

Important APIs/types/functions: Constants define firmware CQ size and TCP defaults such as two-MSL timer, half-way close timeout, FIN retry count, SWS timer, and flow label. `struct qed_nvmetcp_info` owns the connection resource lock, reusable connection free list, outstanding-task limit, and async event callback fields. `struct qed_hash_nvmetcp_con` links active handles into the device hash. `struct qed_nvmetcp_conn` stores ICID/FW CID, queue chains/PBLs, MAC/IP/TCP parameters, update/destroy flags, physical queues, and NVMe/TCP CCCID/ITID table information.

Control flow: The header participates in probe/setup by exposing `qed_nvmetcp_alloc()`, `qed_nvmetcp_setup()`, and `qed_nvmetcp_free()` when `CONFIG_QED_NVMETCP` is enabled. Disabled builds get stubs returning `-EINVAL` or no-op.

State and persistence: It describes all per-connection cached state that persists between user operations and, for free-list entries, across reuse. The fields are copied into firmware ramrods by the implementation rather than directly shared.

Dependencies/integration: Includes Linux list/spinlock helpers, QED chain types, TCP common definitions, public NVMe/TCP interface structs, and core QED SP/MCP definitions.

Risks: Reused `struct qed_nvmetcp_conn` objects need complete reinitialization before offload because the header provides many sticky fields. Disabled-build stubs allow unconditional callers but make runtime feature probing necessary.

Test signals: Build with `CONFIG_QED_NVMETCP=y/m` and disabled, validate structure fields populated by acquire/offload/update paths, and verify free-list reuse does not leak previous digest/TCP/IP/NVMe/TCP settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.c

Purpose: Builds NVMe/TCP firmware task contexts and SQEs for host read, host write, initial connection request, and task cleanup operations.

Important APIs/types/functions: `nvmetcp_is_slow_sgl()` classifies SGLs that require slow-path representation. `init_scsi_sgl_context()` copies SGL address/length metadata and up to four cached SGEs into firmware context. `init_sqe()` fills `struct nvmetcp_wqe` flags, task ID, command/middle-path/cleanup type, continuation length, and SGE count. `init_default_nvmetcp_task()`, `init_ustorm_task_contexts()`, and `init_rw_nvmetcp_task()` initialize E5 storm contexts. Exported functions are `init_nvmetcp_host_read_task()`, `init_nvmetcp_host_write_task()`, `init_nvmetcp_init_conn_req_task()`, and `init_cleanup_task_nvmetcp()`.

Control flow: Read/write setup zeroes the task context while preserving CDU validation, stores opaque and CCCID values, copies/swaps PDU and NVMe command dwords into Y-storm task headers, initializes M-storm/U-storm aggregate/static fields, places SGL metadata in transmit or receive storm context depending on I/O direction, computes expected receive/ack lengths, and optionally marks slow I/O. Login/initial-connection setup uses the non-I/O header size, initializes separate TX/RX SGL contexts if sizes are nonzero, and emits a middle-path SQE. Cleanup only emits a cleanup SQE if an SQE pointer is present.

State and persistence: The functions mutate caller-owned task context and optional SQE memory. They do not allocate or retain resources. Firmware later consumes the initialized context via task IDs and connection ICIDs.

Dependencies/integration: Depends on storage common, NVMe/TCP common HSI layouts, public NVMe/TCP interface task params, endian helpers, `SET_FIELD()` bit macros, and QED-specific header-size constants.

Risks: Header dword copying intentionally byte-swaps command/PDU words for firmware requirements; this is fragile if firmware layout changes. `init_sqe()` may receive `NULL` SGL params for cleanup and must return before dereferencing. Slow-SGL threshold and cached-SGE count must match firmware expectations. Unaligned casts from PDU pointers to `u32 *` assume suitable alignment from callers.

Test signals: Validate read/write/login contexts against firmware HSI golden data, zero-length I/O, incapsule write data, slow-SGL versus cached-SGL paths, IPv-independent header swapping, cleanup with and without SQE, and boundary SGE counts around `SCSI_NUM_SGES_SLOW_SGL_THR` and four cached SGEs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.h

Purpose: Declares NVMe/TCP task-context initialization helpers used by the exported NVMe/TCP core ops table.

Important APIs/types/functions: Under `CONFIG_QED_NVMETCP`, declares host read/write task initializers, initial connection request initializer, and cleanup task initializer. The prototypes use `struct nvmetcp_task_params`, NVMe/TCP PDU types, NVMe command type, and `struct storage_sgl_task_params`.

Control flow: No runtime control flow is implemented here; it gates declarations for call sites in `qed_nvmetcp.c`.

State and persistence: No state is stored. Callers pass all context/SGL/SQE storage.

Dependencies/integration: Includes kernel/QED storage and NVMe/TCP HSI headers so function signatures match firmware context structures.

Risks: The disabled-config branch provides no stubs in this header, so users must compile the function-pointer assignments only when NVMe/TCP support is enabled. Prototype drift from `qed_nvmetcp_fw_funcs.c` would break the ops-table integration.

Test signals: Build coverage with NVMe/TCP enabled and disabled, plus compile checks that `qed_nvmetcp_ops_pass` sees the expected function signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_nvmetcp_fw_funcs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.c

Purpose: Manages software bookkeeping for TCP out-of-order packet buffers. It groups buffers into per-connection ordered "isles", tracks ready/free buffers, records recent OOO CQEs, and supports iSCSI, NVMe/TCP, and iWARP personalities.

Important APIs/types/functions: Allocation/setup/free are `qed_ooo_alloc()`, `qed_ooo_setup()`, and `qed_ooo_free()`. Lookup helpers map CID to an archipelago and numbered isle. Buffer movement APIs include `qed_ooo_put/get_free_buffer()`, `qed_ooo_put/get_ready_buffer()`, `qed_ooo_add_new_isle()`, `qed_ooo_add_new_buffer()`, `qed_ooo_join_isles()`, `qed_ooo_delete_isles()`, `qed_ooo_release_connection_isles()`, and `qed_ooo_release_all_isles()`. `qed_ooo_save_history_entry()` stores a circular history of firmware OOO opaque records.

Control flow: Allocation chooses protocol by PCI personality, sizes archipelagos from protocol CID count, allocates isle entries as `QED_MAX_NUM_ISLES + max_connections`, initializes free lists, allocates archipelago array and history storage, and attaches state to `p_hwfn`. Runtime operations locate the per-CID archipelago by `(cid & 0xffff) - cid_base`, splice buffers between isle, ready, and free lists, and recycle isle descriptors. Joining isle zero moves the right isle into the global ready list; joining a nonzero left isle appends into that left isle.

State and persistence: `p_hwfn->p_ooo_info` owns free/ready/isle lists, archipelago array, isle array, circular history, and counters for current/max/generated isles. Packet buffers own DMA-coherent receive storage and are freed only from the free list during `qed_ooo_free()`.

Dependencies/integration: Depends on QED context manager CID ranges, protocol personality selection, Linux list API, DMA coherent allocation/free, and OOO CQE definitions from the storage/iWARP HSI.

Risks: Most list manipulation has no local locking; callers must serialize access. Isle numbering is one-based in firmware events but implemented through list traversal, so invalid or stale isle numbers just log and return. `qed_ooo_add_new_isle()` initializes an archipelago without validating the computed CID index after failed lookup for isle one. Freeing assumes all buffers eventually return to `free_buffers_list`.

Test signals: Cover allocation for iSCSI, NVMe/TCP, iWARP, and unsupported personalities; add left/right buffers, join isles to ready and to another isle, delete ranges, release one connection/all connections, circular history wrap, and teardown with allocated DMA buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.h

Purpose: Defines OOO buffer/isle/archipelago/history state and declares the OOO management API.

Important APIs/types/functions: `struct qed_ooo_buffer` records list linkage, virtual/physical RX buffer addresses, size, packet length, parse flags, VLAN, and placement offset. `struct qed_ooo_isle` holds an ordered buffer list. `struct qed_ooo_archipelago` holds per-connection isles. `struct qed_ooo_history` stores a circular CQE buffer. `struct qed_ooo_info` aggregates global free/ready/isle lists, arrays, counters, and CID base. The header declares all allocation, release, buffer movement, isle add/delete/join, and history functions, with disabled-config stubs.

Control flow: The header provides build-time selection through `CONFIG_QED_OOO`; disabled builds return `-EINVAL`, `NULL`, or no-op so callers can be compiled conditionally or guarded at runtime.

State and persistence: The structures describe state owned by `p_hwfn->p_ooo_info` and DMA-backed OOO receive buffers. There is no persistence outside memory and firmware event coordination.

Dependencies/integration: Includes QED core definitions, Linux list/slab/types, and references `struct ooo_opaque` from QED HSI.

Risks: The comment in the disabled branch still names iSCSI, but the config is `CONFIG_QED_OOO`. Consumers must not use return values from stubbed buffer getters without checking for `NULL`.

Test signals: Compile with OOO enabled/disabled, validate structure sizing assumptions, and verify all call sites handle stub returns cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ooo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.c

Purpose: Provides low-level Ethernet PTP hardware operations for QED. It enables/disables timestamping hardware, configures packet filters, reads RX/TX timestamps and the PHC counter, and adjusts clock frequency via NIG drift-counter registers.

Important APIs/types/functions: `qed_ptp_ops_pass` exports `cfg_filters`, `read_rx_ts`, `read_tx_ts`, `read_cc`, `adjfreq`, `enable`, and `disable`. `qed_ptcdev_to_resc()`, `qed_ptp_res_lock()`, and `qed_ptp_res_unlock()` map ports to MCP resource locks. Timestamp readers consume NIG host/tx timestamp buffer registers and clear valid bits. `qed_ptp_hw_cfg_filters()` maps `QED_PTP_FILTER_*` and TX mode into NIG rule masks. `qed_ptp_hw_adjfreq()` converts ppb into drift period/value/direction.

Control flow: Enable acquires a PTT, stores it in `p_hwfn->p_ptp_ptt`, acquires the per-port MCP lock or falls back to first-PF ownership for old firmware, resets RX/TX PTP rules, enables timestamping, enables PDA timestamp output, resets the free-running counter through chip-specific registers, disables drift, and clears stale timestamp buffers. Disable releases the MCP lock, resets rules, disables RX/TX PTP, releases the stored PTT, and clears the pointer. Filter configuration writes RX and TX masks and enables based on selected protocol family. Frequency adjustment searches 1..7 ns adjustment values for the best approximation and programs drift registers after reset.

State and persistence: The main persistent state is `p_hwfn->p_ptp_ptt`, held between enable and disable, plus hardware NIG timestamp/filter/drift registers and MCP resource-lock ownership.

Dependencies/integration: Depends on QED hardware register accessors, MCP resource locking, PTT management, chip-family helpers (`QED_IS_BB_B0`, `QED_IS_AH`), PTP enums from the Ethernet API, and numerous `NIG_REG_*` addresses from `qed_reg_addr.h`.

Risks: Holding a PTT across the enabled lifetime makes cleanup ordering important. Old MFW lock fallback grants ownership only to early PFs by `abs_pf_id`, so multi-PF behavior differs by firmware. `qed_ptp_hw_disable()` assumes `p_ptp_ptt` is valid. The ppb algorithm has special handling for 1 ppb and integer limits. Filter masks are magic constants and easy to regress.

Test signals: Enable/disable on supported and unsupported PFs, MFW lock grant/deny/unsupported paths, all RX filter modes with TX on/off, invalid filter rejection, RX/TX timestamp valid-bit handling and clear, PHC read monotonicity, positive/negative/zero/1 ppb adjustment, and chip-specific free-counter reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.h

Purpose: Declares the QED Ethernet PTP operations table exported by `qed_ptp.c`.

Important APIs/types/functions: `extern const struct qed_eth_ptp_ops qed_ptp_ops_pass;` is the only declaration.

Control flow: No runtime logic; consumers bind to the ops table when PTP support is available in the Ethernet-facing QED API.

State and persistence: No state is stored in the header.

Dependencies/integration: Requires `struct qed_eth_ptp_ops` to be visible through prior QED Ethernet headers at inclusion sites.

Risks: The header has no config stubs, so build configuration must ensure only valid consumers reference the symbol.

Test signals: Compile/link coverage for Ethernet driver paths that include PTP ops and for builds where PTP object code is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.c

Purpose: Implements the generic QED RDMA operations layer shared by RoCE and iWARP. It allocates RDMA resource maps, starts/stops firmware RDMA functions, exposes device/port/interrupt information, manages PD/DPI/CQ/QP/MR/SRQ resources, and exports `qed_get_rdma_ops()`.

Important APIs/types/functions: Bitmap helpers (`qed_rdma_bmap_alloc()`, `qed_rdma_bmap_alloc_id()`, `qed_bmap_release_id()`, `qed_bmap_test_id()`) back all ID allocators. Lifecycle helpers are `qed_rdma_info_alloc/free()`, `qed_rdma_alloc()`, `qed_rdma_setup()`, `qed_rdma_start_fw()`, `qed_rdma_start()`, and `qed_rdma_stop()`. Public resource operations cover user DPI add/remove, PD/XRCD allocation, CQ create/destroy, QP create/modify/query/destroy, TID allocate/free/register/deregister, SRQ create/modify/destroy, CNQ producer updates, LL2 bridging, DPM configuration, and iWARP engine affinity.

Control flow: Start acquires a PTT, allocates per-protocol resource bitmaps based on context-manager CID/TID counts, initializes device/port/events, reserves TID 0 as the reserved lkey, initializes RoCE or iWARP hardware, registers protocol-specific setup, and posts an RDMA function-init ramrod with CNQ PBLs/SB IDs/queue zones. CQ creation allocates an ICID from `cq_map`, dynamically allocates ILT context, toggles the CQ toggle bit, and posts create-CQ; destroy posts a destroy-CQ with DMA output and releases the ID. QP create allocates and fills `struct qed_rdma_qp`, delegates CID/offload setup to iWARP or RoCE, and returns QP IDs. Modify updates cached QP fields based on validity flags and delegates state transitions. MR/TID registration posts firmware ramrods with access flags and PBL information; deregistration can run an MCP drain and retry when firmware requests it. Stop disables parser search and light-L2 ethertype, stops protocol-specific state, posts close-function, and frees RDMA resources.

State and persistence: `p_hwfn->p_rdma_info` stores spinlock-protected bitmaps for CQ/PD/XRCD/TID/SRQ/XRC-SRQ/CID/real-CID/DPI/toggle bits, protocol type, device/port snapshots, event callbacks, queue-zone base, counts, last TID, number of CNQs, iWARP state, and active flag. QP structs persist across user QP operations and cache firmware-visible state. Hardware/parser/DORQ/queue-zone registers and firmware contexts persist until stop/destroy.

Dependencies/integration: Depends on QED context/ILT manager, SPQ ramrods, interrupt/MSI-X allocation, LL2 ops, MCP drain, DCB/DPM doorbell registers, RoCE and iWARP modules, Linux RDMA public interface structs, PCI capability reads, and GTT/USTORM producer register access.

Risks: Bitmap alloc/free paths are central; leaks are logged during teardown but can leave feature stop noisy or unsafe. Several allocators set output IDs even when allocation fails, so callers must honor return codes. `qed_rdma_alloc_tid()` does not release the TID bit if dynamic ILT allocation fails. Stop frees resources even after close-ramrod errors. QP state is cached in software and must stay consistent with RoCE/iWARP ramrod success. CNQ producer update only checks `>` rather than `>=` against `max_queue_zones`. MSI-X is mandatory.

Test signals: Start/stop with RoCE and iWARP personalities, fault injection through each bitmap/ILT/SPQ allocation path, reserved lkey enforcement, CQ create/destroy and resize toggle-bit behavior, QP state transitions and invalid inputs, MR register/deregister including NIG drain retry, SRQ/XRC SRQ offsets, DPI doorbell address calculation, MSI-X setup/query, DPM changes on DCBX/DB BAR events, and teardown leak warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.h

Purpose: Defines internal RDMA resource, device, and QP state shared by the generic RDMA layer plus RoCE/iWARP implementations.

Important APIs/types/functions: Constants encode RDMA limits for PKEYs, WQEs, SRQs, page sizes, ACK delay, MR size, CQE modes, and XRCD count. `struct qed_bmap` wraps a named bitmap. `struct qed_rdma_info` stores all RDMA bitmaps, event callbacks, device/port pointers, resource counts, protocol, queue-zone data, and active flag. `struct qed_rdma_qp` stores software-visible QP state, handles, IDs, access flags, address vectors, requester/responder PBLs and DMA memory, SRQ/XRC fields, MACs, and iWARP/EDPM fields. Inline `qed_rdma_is_xrc_qp()` identifies XRC QP types. Public internal declarations expose DPM, info alloc/free, bitmap helpers, MAC conversion, and allocated-QP detection.

Control flow: Build-time `CONFIG_QED_RDMA` stubs allow non-RDMA builds to compile core callers. The data structures are filled by `qed_rdma.c` and consumed heavily by `qed_roce.c`/`qed_iwarp.c`.

State and persistence: The header describes the long-lived per-hwfn RDMA state and per-QP state that survive across API calls until stop/destroy.

Dependencies/integration: Includes public QED RDMA interface, QED device/core/HSi headers, and iWARP/RoCE headers, making it the bridge between common RDMA code and protocol-specific modules.

Risks: Structure fields encode firmware assumptions such as paired RoCE CIDs, reserved lkey, page counts, and queue-zone layout. Disabled stubs return `-EINVAL`, so callers need feature checks. The header includes both iWARP and RoCE types, increasing coupling and recompilation scope.

Test signals: Compile with RDMA enabled/disabled, validate QP field initialization for RoCE and iWARP, bitmap naming/size limits, XRC QP detection, and DPM stub behavior in non-RDMA builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_rdma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_reg_addr.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_reg_addr.h

Purpose: Central register-address and bitfield-definition header for the QED driver. It gives implementation files symbolic names for BAR0/GRC block registers, memory windows, debug controls, parser/NIG/DORQ/QM/IGU/CDU/Storm registers, MCP scratch/shared memory offsets, tunnel configuration registers, PTP timestamp registers, RDMA parser registers, and many chip-specific variants.

Important APIs/types/functions: There are no functions or types; the file is a large set of `#define` constants. Important groups include context/CDU CID/TID parameter masks, BAR0 storm RAM maps, MCP scratch/public memory, NIG LLH/filter/PTP/tunnel registers, PRS parser search and light-L2/RoCE registers, DORQ doorbell/EDPM registers, IGU interrupt/status/configuration registers, QM rate-limit/WFQ/PQ registers, PGLUE error/BAR registers, debug select/shift/force registers for many blocks, and block init/soft-reset addresses.

Control flow: No runtime control flow. Consumers use these constants with `qed_rd()`, `qed_wr()`, `REG_WR16()`, GTT address macros, and bitfield helpers to program hardware.

State and persistence: The header itself stores no state. Values correspond to persistent hardware register locations and bit masks whose effects last until hardware reset or later programming.

Dependencies/integration: Included throughout QED core, storage, RDMA, PTP, LLH, debug, init, and MCP paths. Files in this work item use it for PTP NIG registers, RDMA parser/light-L2/DORQ registers, MCP TLV shared memory access, and NVMe/TCP doorbell/PQ context.

Risks: Register constants are an ABI with hardware/firmware. Wrong addresses, duplicate names, chip-family mismatches, or mask/shift drift can cause silent hardware misprogramming. Because this header is broad and untyped, invalid combinations are caught only through hardware behavior or focused tests. Some names have BB/K2/E5 suffixes while others are generic, so call sites must choose by chip helper when needed.

Test signals: Compile coverage across all QED personalities, hardware bring-up smoke tests, register read/write selftests, PTP timestamp/filter tests, RDMA/RoCE parser enable tests, tunnel and LLH filter tests, debug dump paths, and static checks for duplicate/mismatched mask/shift pairs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_reg_addr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.c

Purpose: Implements RoCE-specific RDMA operations behind the generic `qed_rdma.c` layer. It manages paired responder/requester CIDs, programs RoCE QP create/modify/query/destroy ramrods, handles async RoCE events, configures parser prerequisites, and reacts to DCBX changes affecting DPM.

Important APIs/types/functions: `qed_roce_alloc_cid()` allocates adjacent responder/requester CIDs and ILT context. `qed_roce_sp_create_responder()` and `qed_roce_sp_create_requester()` allocate IRQ/ORQ pages and post create-QP ramrods. `qed_roce_sp_modify_responder()` and `qed_roce_sp_modify_requester()` post modify ramrods. `qed_roce_query_qp()`, `qed_roce_modify_qp()`, and `qed_roce_destroy_qp()` implement public protocol hooks. `qed_roce_free_real_icid()` releases real-CID and paired CID bitmap state after async destroy. `qed_roce_setup()` registers the async callback; `qed_roce_init_hw()` enables RoCE parsing prerequisites; `qed_roce_stop()` waits for outstanding real CIDs.

Control flow: QP creation in the generic layer allocates a software QP and calls `qed_roce_alloc_cid()` but does not offload until state transitions. INIT/RESET to RTR creates the responder, allocating IRQ memory and marking the responder real CID. RTR to RTS creates the requester, allocating ORQ memory, then modifies responder fields. RTS/SQD modifications post the appropriate responder/requester ramrods. Moving to ERR posts error modifies for offloaded halves. Moving to RESET destroys responder and requester, freeing IRQ/ORQ only after successful ramrods; firmware later emits destroy-QP async events that clear real-CID bits and finally free the paired CID-map entries. Query uses DMA output buffers to fetch PSN/error/draining state from offloaded halves.

State and persistence: RoCE uses `qed_rdma_qp` fields for cached address vector, PSNs, flags, DMA pages, offloaded booleans, CQ producer, and paired CIDs. `p_rdma_info->cid_map` reserves software QP pairs; `real_cid_map` tracks halves currently offloaded to firmware. Parser/light-L2 register settings persist until RDMA stop.

Dependencies/integration: Depends on generic RDMA bitmaps/state, SPQ ramrods, context manager ILT allocation, DCBX priority-to-TC mapping, CM PQ selection, MAC conversion helper, LL2/parser register definitions, and RDMA event callbacks into the upper protocol driver.

Risks: RoCE requires adjacent CIDs and even protocol CID start; allocation error cleanup mixes relative and absolute CID values and is sensitive to start-CID arithmetic. Async destroy is required to free real CIDs; `qed_roce_stop()` waits up to about two seconds unless recovery is in progress. DMA IRQ/ORQ memory is freed only after successful destroy ramrods to avoid firmware use-after-free, so failure paths can retain resources until later cleanup. Query rejects requester-offloaded without responder-offloaded as inconsistent. VLAN priority controls TC/PQ choice only when a VLAN ID is present.

Test signals: Adjacent CID allocation, odd CID-start rejection, INIT/RTR/RTS/SQD/ERR/RESET transitions, XRC initiator/target QPs, RoCE v1/v2 IPv4/v2 IPv6 GID packing, VLAN-priority TC mapping, async destroy event handling, stop timeout/recovery behavior, query of non-offloaded and half-offloaded QPs, create/destroy ramrod fault injection, and DCBX DPM disable when QPs are allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.h

Purpose: Declares RoCE-specific hooks consumed by the generic RDMA layer and DCBX code.

Important APIs/types/functions: Exposes `qed_roce_dpm_dcbx()`, `qed_roce_setup()`, `qed_roce_stop()`, `qed_roce_init_hw()`, `qed_roce_alloc_cid()`, `qed_roce_destroy_qp()`, `qed_roce_query_qp()`, and `qed_roce_modify_qp()`. `qed_roce_dpm_dcbx()` has a no-op stub when `CONFIG_QED_RDMA` is disabled.

Control flow: No implementation logic; it defines the protocol-specific call surface invoked during RDMA start/stop and QP state transitions.

State and persistence: No direct state. Functions operate on `struct qed_hwfn` and `struct qed_rdma_qp` state defined elsewhere.

Dependencies/integration: Includes Linux types/slab and relies on QED RDMA structures being declared before use in compilation units.

Risks: Most declarations are not config-stubbed, so non-RDMA builds must avoid linking users of the full RoCE API. The header forms a circular conceptual dependency with `qed_rdma.h`, which includes it while also defining `struct qed_rdma_qp`.

Test signals: Build with RDMA enabled/disabled, verify generic RDMA code links all RoCE symbols in enabled builds, and confirm DCBX code can call `qed_roce_dpm_dcbx()` unconditionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_roce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.c

Purpose: Implements QED diagnostic selftests for memory, interrupts, register BIST, clock BIST, and NVRAM image CRC validation.

Important APIs/types/functions: `qed_selftest_memory()` and `qed_selftest_interrupt()` both issue `qed_sp_heartbeat_ramrod()` on every hwfn. `qed_selftest_register()` and `qed_selftest_clock()` acquire a PTT per hwfn and call MCP BIST commands. `qed_selftest_nvram()` gets image count and attributes from MCP, reads each NVM image except MDUMP, endian-normalizes the image payload, computes CRC32, and compares with the stored trailer CRC.

Control flow: Per-engine tests iterate `for_each_hwfn()` and fail fast on the first error. Register/clock tests acquire/release PTT around each MCP call. NVRAM test uses the leading hwfn, acquires one PTT, queries image metadata, allocates a buffer per image, reads NVM contents, converts all dwords except the final CRC to big-endian form, computes inverted big-endian CRC32, frees each buffer before the next image, and releases PTT on all exits.

State and persistence: No persistent driver state is modified. Tests temporarily allocate image buffers, use PTT resources, and invoke firmware diagnostics. NVRAM reads are non-mutating.

Dependencies/integration: Depends on SP heartbeat ramrod, MCP BIST/NVM APIs, PTT management, Linux CRC32, QED logging, and NVM image type definitions.

Risks: Memory and interrupt tests are currently identical heartbeat checks, so they may not distinguish failure classes. NVRAM test assumes image length is at least four bytes and dword-aligned for conversion. MDUMP images are skipped because crash dumps invalidate CRC. Large NVM images can cause large `kzalloc()` allocations.

Test signals: Heartbeat success/failure on each hwfn, PTT acquisition failure, MCP register/clock BIST failures, NVRAM no-image path, image attribute/read errors, MDUMP skip, CRC mismatch, endian conversion correctness, and allocation failure for large images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.h

Purpose: Declares the QED selftest API used by higher-level driver diagnostics.

Important APIs/types/functions: Exposes `qed_selftest_memory()`, `qed_selftest_interrupt()`, `qed_selftest_register()`, `qed_selftest_clock()`, and `qed_selftest_nvram()`, all taking `struct qed_dev *` and returning an integer status.

Control flow: No runtime logic. Kernel-doc comments describe each diagnostic entry point.

State and persistence: No state is stored in the header.

Dependencies/integration: Includes Linux types and relies on `struct qed_dev` being declared by including contexts.

Risks: The header does not provide disabled-build stubs, so link coverage must match object inclusion. Comments use generic `Return: Int.` and do not document specific negative errno values.

Test signals: Compile/link diagnostics consumers and verify each declared function is reachable from ethtool or equivalent selftest paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qed/qed_selftest.h -->
