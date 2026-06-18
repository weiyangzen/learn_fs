# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_isr.c

## Purpose

`qla_isr.c` is the interrupt, asynchronous-event, and response-completion core for the QLogic/Marvell `qla2xxx` Fibre Channel HBA driver. It translates legacy INTx/MSI and MSI-X hardware interrupts into mailbox completions, asynchronous event handling, response queue draining, target-mode ATIO work, and SCSI/NVMe/ELS/CT/management command completion.

The file bridges firmware IOCB formats to Linux subsystems. It completes SCSI commands through `srb_t->done`, reports FC link and fabric events to the driver DPC and FC transport, delivers FPIN notifications to the FC host, routes target-mode IOCBs into `qla_target`, handles FC-NVMe completions and unsolicited LS requests, and owns IRQ vector allocation/freeing for the adapter.

## Important APIs, Types, And Functions

Core interrupt entry points are `qla2100_intr_handler()`, `qla2300_intr_handler()`, `qla24xx_intr_handler()`, `qla24xx_msix_rsp_q()`, `qla24xx_msix_default()`, and `qla2xxx_msix_rsp_q()`. They are selected by chip generation and IRQ mode. `qla2x00_request_irqs()`, `qla24xx_enable_msix()`, `qla2x00_free_irqs()`, and `qla25xx_request_irq()` allocate vectors, bind handlers, and tear them down.

Response queue processing is split between legacy `qla2x00_process_response_queue()` and FWI2 `qla24xx_process_response_queue()`. Both advance `struct rsp_que` ring pointers, mark IOCBs with `RESPONSE_PROCESSED`, use write barriers before notifying firmware, and dispatch by IOCB `entry_type`.

Mailbox and AEN handling is centered on `qla2x00_mbx_completion()`, `qla24xx_mbx_completion()`, `qla2x00_handle_mbx_completion()` from elsewhere, and `qla2x00_async_event()`. AEN cases update loop/link state, schedule DPC bits, post FC host events, process IDC/MPI/NIC-core failures, handle D-Port diagnostics, temperature/transceiver notices, RSCNs, port updates, and propagate events to target-mode and virtual ports.

Command lookup and completion helpers include `qla_get_sp_from_handle()`, `qla2x00_get_sp_from_handle()`, `qla2x00_process_completed_request()`, `qla2x00_status_entry()`, `qla2x00_status_cont_entry()`, and `qla2x00_error_entry()`. These map firmware handles back to request queues and `srb_t` objects, release firmware resources, remove outstanding command slots, and call the SRB completion callback with Linux SCSI result codes or driver-specific status.

IOCB-specific completion handlers include `qla2x00_mbx_iocb_entry()`, `qla24xx_mbx_iocb_entry()`, `qla24xx_logio_entry()`, `qla24xx_tm_iocb_entry()`, `qla24xx_nvme_iocb_entry()`, `qla24xx_els_ct_entry()`, `qla2x00_ct_entry()`, `qla24xxx_nack_iocb_entry()`, `qla24xx_abort_iocb_entry()`, `qla24xx_nvme_ls4_iocb()`, `qla_ctrlvp_completed()`, `qla_marker_iocb_entry()`, and `qla25xx_process_bidir_status_iocb()`.

Unsolicited frame handling uses `struct purex_item`, `qla24xx_alloc_purex_item()`, `qla24xx_queue_purex_item()`, `qla24xx_copy_std_pkt()`, `qla27xx_copy_fpin_pkt()`, `qla27xx_copy_multiple_pkt()`, `__qla_consume_iocb()`, and `__qla_copy_purex_to_buffer()`. ABTS and FPIN paths are handled by `qla24xx_process_abts()` and `qla27xx_process_purex_fpin()`.

The important state-bearing types from included headers are `scsi_qla_host_t`, `struct qla_hw_data`, `struct rsp_que`, `struct req_que`, `struct qla_qpair`, `srb_t`, `fc_port_t`, firmware IOCB structs such as `sts_entry_t`, `sts_entry_24xx`, `purex_entry_24xx`, `logio_entry_24xx`, `mbx_entry`, `mbx_24xx_entry`, `pt_ls4_request`, and Linux types such as `struct scsi_cmnd`, `struct bsg_job`, `struct fc_bsg_reply`, and `struct nvmefc_fcp_req`.

## Control Flow

Legacy 2100/2200 and 2300 interrupt handlers run under `ha->hardware_lock`, poll host status up to a bounded iteration count, detect PCI disconnect values, handle RISC pause by dumping firmware and setting `ISP_ABORT_NEEDED`, then classify the interrupt as mailbox completion, asynchronous event, or response queue update. They clear RISC interrupts through generation-specific registers and finish by calling `qla2x00_handle_mbx_completion()`.

The 24xx/FWI2 interrupt path follows the same high-level sequence but uses 32-bit `host_status` and FWI2 interrupt codes. `qla24xx_intr_handler()` can process response queues, defer ATIO work until after dropping `hardware_lock`, and call `qlt_24xx_process_atio_queue()` under `ha->tgt.atio_lock`. MSI-X splits default/mailbox/AEN handling from response-queue handling. The qpair multi-queue MSI-X handler only queues `qpair->q_work` on `ha->wq`, leaving response processing to workqueue context.

Response queue draining advances the software ring before dispatching the current IOCB. On legacy queues, `qla2x00_process_response_queue()` loops until the current entry signature is already processed and writes `ISP_RSP_Q_OUT`. On FWI2 queues, `qla24xx_process_response_queue()` reads the firmware producer index from a shadow register or MMIO, handles continuation availability for multi-IOCB PUREX/PURLS payloads, and writes the response queue out index through the proper 82xx or FWI2 register.

The FWI2 dispatch table is broad. SCSI/NVMe status goes to `qla2x00_status_entry()`. Continuation status extends pending sense data. Login/logout, ELS, CT, mailbox, abort, marker, notify-ack, VP control, LS4, and SA update IOCBs go to their specialized completion handlers. Target-mode packets are routed through `qlt_response_pkt_all_vps()`, `qlt_handle_abts_recv()`, or ATIO processing. PUREX entries are interpreted by ELS opcode: RDP and FPIN are copied to `purex_item` work, authentication ELS is deferred until all continuations arrive and then handled by `qla24xx_auth_els()`, and unknown ELS requests are discarded with a warning.

`qla2x00_status_entry()` is the main SCSI/NVMe completion path. It extracts request queue and handle from the firmware handle, validates the queue, releases firmware resources, and branches for NVMe, bidirectional BSG, task management, and normal SCSI. Fast successful SCSI completions use `qla2x00_process_completed_request()`. Non-fast completions decode FCP response information, sense data, residuals, DIF errors, transport failures, underrun/overrun, queue-full/busy status, and port-loss conditions before calling `sp->done()` and clearing `req->outstanding_cmds[handle]`.

`qla24xx_nvme_iocb_entry()` maps FWI2 status into FC-NVMe completion state. It updates active AEN and qpair completion counters, computes transferred length, handles DMAed or embedded NVMe ERSP data, checks for dropped frames by comparing target-reported transfer length, marks resetting ports on link/port failures, and completes the SRB with `QLA_SUCCESS`, `QLA_ABORTED`, or `QLA_FUNCTION_FAILED`.

AEN control flow in `qla2x00_async_event()` first normalizes fast-post completion mailbox formats into command handles where applicable. It then updates driver state for resets, system errors, request/response transfer errors, loop up/down, LIP/LIP reset, point-to-point mode, connection changes, port updates, RSCNs, congestion notifications, ZIO responses, DCBX/FCF events, IDC events, MPI/NIC heartbeat failures, D-Port diagnostics, temperature alerts, and transceiver insertion/removal. Most disruptive conditions set bits in `vha->dpc_flags` for deferred recovery rather than performing recovery directly in interrupt context.

PUREX and continuation control flow is deliberately two-stage. The interrupt path copies or consumes all IOCB fragments, marks them processed with barriers, optionally swaps byte order, queues a `purex_item` on `vha->purex_list`, and sets `PROCESS_PUREX_IOCB` for deferred processing. FPIN is delivered with `fc_host_fpin_rcv()`. ABTS received in initiator mode is copied and later answered by issuing ELS/ABTS response IOCBs through `qla2x00_issue_iocb()`.

## State And Persistence Behavior

The file has no filesystem persistence. All state is volatile adapter, queue, command, FC-port, virtual-port, and workqueue state.

The persistent runtime anchors are `struct qla_hw_data` and `scsi_qla_host_t`. This file mutates `ha->flags` fields such as `mbox_int`, `fw_init_done`, `lip_ae`, `msix_enabled`, `msi_enabled`, `mqenable`, `nic_core_hung`, and IDC status; it updates link rate/topology and hardware error counters; and it stores mailbox completion values in `ha->mailbox_out[]`. On the vhost it changes `vha->flags.online`, management-server login state, `device_flags`, `dpc_flags`, `vp_flags`, `loop_state`, `loop_down_timer`, `vp_state`, D-Port data, link-down counters, and interface error counters.

Response queue state is maintained in `rsp->ring_ptr`, `rsp->ring_index`, `rsp->status_srb`, MMIO/shadow in-pointers, and firmware-visible out-pointers. Each response entry is marked consumed by writing `RESPONSE_PROCESSED` into the entry signature followed by `wmb()`. Request queue state is maintained in `req->outstanding_cmds[]`; most completion paths clear the slot before or after calling `sp->done()`, depending on whether extra continuation data is pending.

Per-command state resides in `srb_t`, its embedded `struct srb_iocb`, and the owned Linux command or BSG/NVMe request. Completion handlers update mailbox/logio data arrays, ELS/CT reply lengths and status, SCSI residual and sense buffers, NVMe response payload metadata, task-management result fields, and vendor BSG reply status.

Per-port state is updated opportunistically from completions and AENs. Login completions set `fc_port_t` type, FCP2/FCSP/conf-completion flags, supported classes, and IO parameters. Transport failures and port logout/configuration changes can schedule session deletion through `qlt_schedule_sess_for_deletion()`. RSCN and port-update events drive loop resync and device-lost marking.

IRQ allocation state is stored in PCI IRQ vectors and `ha->msix_entries[]`. `qla24xx_enable_msix()` may reduce queue counts if fewer vectors are available, records vector names/handles, and enables multi-queue mode only when the hardware and vector layout support it. `qla2x00_free_irqs()` reverses this and clears MSI-X state.

## Dependencies And Integration Points

This file depends on qla2xxx internal definitions from `qla_def.h`, target-mode interfaces from `qla_target.h`, and global prototypes/helpers from `qla_gbl.h`. It uses chip capability macros, MMIO register accessors, mailbox accessors, IOCB structs, DPC flag definitions, logging/debug helpers, and firmware operation callbacks such as `fw_dump()` and `mpi_fw_dump()`.

Linux SCSI integration appears through `struct scsi_cmnd`, SCSI result codes, residual/sense helpers, queue-full/busy handling, T10 PI/DIF APIs, and BSG FC passthrough reply structures. FC transport integration includes host event posting, vport state updates, WWPN restoration, RSCN handling, and FPIN delivery through `fc_host_fpin_rcv()`. FC-NVMe integration uses `struct nvmefc_fcp_req` and NVMe ERSP IU handling.

Target-mode integration is frequent but implemented elsewhere. This file routes ABTS, CTIO, notify-ack, ATIO, and generic target response packets into `qlt_*` helpers, calls `qlt_async_event()` for every AEN, alerts virtual ports with `qla2x00_alert_all_vps()`, and schedules target sessions for deletion on port-loss signals.

Hardware and kernel infrastructure dependencies include PCI EEH/disconnect detection, PCI MSI/MSI-X vector allocation, IRQ registration/freeing, IRQ affinity setup for qpairs, spinlocks, atomics, workqueues, DMA coherent allocation for ABTS responses, endian conversion helpers, memory barriers, microsecond/nanosecond delays, and scatterlist copy helpers for remapped ELS responses.

## Risks And Edge Cases

Interrupt handlers run under `ha->hardware_lock`, so any new work in those paths must avoid sleeping and keep register ordering intact. Several recovery actions are intentionally deferred through DPC flags; doing reset, login, or allocation-heavy work inline would risk deadlocks or interrupt latency problems.

Queue and handle validation is central to correctness. Invalid handles trigger ISP/FCoE context reset scheduling; stale or already-completed handles are logged and ignored. Any path that clears `req->outstanding_cmds[]` at the wrong time can cause double completion, leaked commands, or timeout recovery racing with a late firmware completion.

Response ring accounting is fragile because the consumer pointer is advanced before processing. PUREX/PURLS multi-IOCB paths may temporarily rewind `ring_ptr` and `ring_index` if continuations have not arrived. Incorrect continuation counts, missing `wmb()`, or failure to update `rsp_q_in` after copying continuations can desynchronize firmware and driver ownership of the ring.

Sense continuation handling keeps a pending `rsp->status_srb` and delays final completion until all sense bytes arrive. If a later status continuation is lost, malformed, or associated with a command already returned to the OS, the path can leave incomplete diagnostic data or must drop the pending state defensively.

SCSI status translation has many special cases: firmware residual versus FCP residual mismatches are treated as dropped frames, underflow is compared to `cmd->underflow`, busy/queue-full can program retry delay timestamps, and DIF errors may patch protection tags for escape cases before synthesizing sense. Changes here can directly alter Linux mid-layer retry and error-recovery behavior.

NVMe completion handling trusts a mix of state flags, DMAed response buffers, and embedded response payloads. Incorrect byte swapping or response length handling can corrupt ERSP data. The dropped-frame comparison between `fd->transferred_length` and target-reported `xfrd_len` is an important data-integrity signal.

AEN handling mutates global link, loop, vport, and session state from many mailbox codes. Filtering by vport index, skipping RSCNs for sibling virtual ports, restoring FA-WWPN on loop down, and differentiating recoverable from unrecoverable IDC/NIC/MPI failures are all hardware- and topology-sensitive.

MSI-X setup recalculates queue limits when fewer vectors are allocated than requested. Multi-queue, target-mode ATIO vectors, user-controlled IRQ settings, and qpair CPU mapping interact; regression here can leave queues without interrupts or reduce queue counts inconsistently with earlier allocation.

## Test Signals

Build coverage should include representative qla2xxx configurations with SCSI, BSG, target mode, FC-NVMe, NPIV, T10 PI, MSI, MSI-X, multi-queue, and 82xx/83xx/27xx/28xx chip capability paths enabled. Static analysis should pay attention to IRQ-context sleeping, endian conversions, ring index arithmetic, and outstanding-command slot ownership.

Interrupt tests should exercise legacy INTx/MSI and MSI-X default/response/qpair vectors, mailbox success/failure completions, async events, response queue updates, ATIO-only updates, combined ATIO/response updates, RISC pause, PCI disconnect reads returning all ones, and fallback from MSI-X to MSI/INTx.

Response queue tests should cover `STATUS_TYPE`, `STATUS_CONT_TYPE`, login/logout, CT, ELS, mailbox IOCB, abort IOCB, notify-ack, marker, VP control, LS4, SA update, ABTS receive/response, CTIO, PUREX RDP/FPIN/authentication ELS, PURLS, unknown IOCB types, entry-status error paths, and incomplete continuation deferral.

SCSI completion tests should include clean completion, check condition with inline and continuation sense, data underrun and overrun, mid-layer underflow, queue full, busy, port logged out, port unavailable, timeout, reset, abort, DMA error, transport error, DIF guard/ref/app-tag mismatches, and stale or invalid handles.

NVMe tests should cover successful FCP requests, AEN counter decrement, embedded ERSP copying, DMAed ERSP, unexpected NVMe_RSP IU state, oversized ERSP length clamping, dropped-frame detection, data underrun without loss, abort/reset/port-loss statuses, and abort IOCB completion propagation to the original SRB.

AEN tests should inject loop up/down, LIP, LIP reset, point-to-point, connection change, port logout/global port update, RSCN including local-host and sibling-vport DIDs, congestion warning/alarm, IDC notify/complete/time extension, 83xx NIC-core failures, 27xx MPI heartbeat stop, D-Port diagnostic outcomes, temperature laser disable/enable, transceiver insertion/removal, and ZIO response queue updates.

IRQ lifecycle tests should verify vector allocation names and handles, reduced-vector queue recalculation, target-mode ATIO vector registration, qpair `request_irq()` plus CPU mapping, cleanup after partial registration failure, `qla2x00_free_irqs()` after probe failure, and no leaked vectors across remove/reprobe.
