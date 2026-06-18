# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.c

## Purpose
`qla_mr.c` implements the QLogic/Marvell FX00 multi-role adapter support inside the `qla2xxx` SCSI/Fibre Channel driver. It supplies FX00-specific mailbox command transport, PCI/MMIO setup, firmware readiness and reset recovery, target discovery, host-information registration, asynchronous event processing, response queue parsing, SCSI command IOCB construction, task-management and abort IOCB construction, and vendor FXDISC/BSG IOCB handling.

The file is hardware-facing. Most routines translate generic `qla2xxx` driver operations into FX00 register accesses, FX00 IOCB layouts from `qla_mr.h`, and firmware discovery commands.

## Important APIs, Types, And Functions
The mailbox core is `qlafx00_mailbox_command()`, which serializes mailbox access with `ha->mbx_cmd_comp`, writes 32-bit mailbox registers, rings `QLAFX00_SET_HST_INTR()`, waits by interrupt or polling, copies returned mailbox values from `ha->mailbox_out32`, and schedules or directly invokes ISP abort recovery on timeout.

Adapter initialization and low-level setup are handled by `qlafx00_pci_config()`, `qlafx00_iospace_config()`, `qlafx00_soft_reset()`, `qlafx00_chip_diag()`, `qlafx00_initialize_adapter()`, `qlafx00_init_fw_ready()`, `qlafx00_fw_ready()`, `qlafx00_config_rings()`, `qlafx00_save_queue_ptrs()`, and `qlafx00_config_queues()`. These routines map BAR0/BAR2, configure PCI command bits, wait for firmware AEN mailbox state, bind request/response rings to firmware-provided BAR2 offsets, and initialize outstanding command tracking.

Firmware and management commands include `qlafx00_driver_shutdown()`, `qlafx00_get_firmware_state()`, `qlafx00_init_firmware()`, `qlafx00_mbx_reg_test()`, `qlafx00_fx_disc()`, `qlafx00_fw_state_show()`, and `qlafx00_get_host_speed()`. `qlafx00_fx_disc()` is the central discovery/vendor-command helper and supports config info, port info, target-node info/list, host-info registration, and ioctl abort completion normalization.

Discovery and target database flow is split across `qlafx00_configure_devices()`, `qlafx00_configure_all_targets()`, `qlafx00_find_all_targets()`, `qlafx00_get_fcport()`, and `qlafx00_tgt_detach()`. It scans the firmware target bitmap, fetches target WWNs, updates existing `fc_port_t` entries, adds new ones, and marks missing devices lost.

Reset, timer, and AEN paths include `qlafx00_abort_isp()`, `qlafx00_reset_initialize()`, `qlafx00_abort_isp_cleanup()`, `qlafx00_rescan_isp()`, `qlafx00_timer_routine()`, `qlafx00_process_aen()`, and `qlafx00_async_event()`. These coordinate firmware heartbeat misses, reset-recovery AEN polling, critical-temperature recovery, link/port-update events, and DPC wakeups.

Interrupt and response processing are in `qlafx00_intr_handler()`, `qlafx00_mbx_completion()`, `qlafx00_process_response_queue()`, `qlafx00_status_entry()`, `qlafx00_status_cont_entry()`, `qlafx00_multistatus_entry()`, `qlafx00_abort_iocb_entry()`, `qlafx00_ioctl_iosb_entry()`, and `qlafx00_error_entry()`. These turn FX00 response IOCBs into SCSI completion, task-management completion, BSG replies, or recovery triggers.

IO submission helpers include `qlafx00_start_scsi()`, `qlafx00_build_scsi_iocbs()`, `qlafx00_prep_cont_type1_iocb()`, `qlafx00_tm_iocb()`, `qlafx00_abort_iocb()`, and `qlafx00_fxdisc_iocb()`. They allocate handles, map SG lists, build `cmd_type_7_fx00`, continuation, task-management, abort, and FXDISC IOCBs, then ring the FX00 request doorbell.

## Control Flow
Initialization starts with PCI and IO-space setup. BAR0 becomes `ha->cregbase` for control registers and BAR2 becomes `ha->iobase` for the FX00 device-register and ring region. `qlafx00_init_fw_ready()` watches AEN mailbox registers for firmware startup states. On `MBA_FW_RESTART_CMPLT`, it records mailbox/request interrupt codes and queue offsets/lengths, clears interrupt status, and allows ring setup. If firmware is in an unexpected state, it reloads shadow initialization values, queries firmware state, and may request driver shutdown before retrying.

`qlafx00_initialize_adapter()` clears volatile driver flags, initializes queue-id maps, configures PCI space, waits for firmware readiness, preserves original queue pointers, replaces ring pointers with firmware-provided BAR2 offsets, allocates outstanding command arrays, initializes rings, and records current SoC temperature. `qlafx00_fw_ready()` later polls firmware state until `FSTATE_FX00_INITIALIZED`.

Mailbox commands flow through `qlafx00_mailbox_command()`: wait for exclusive mailbox access, write outgoing mailboxes under `hardware_lock`, set `MBX_INTR_WAIT` when interrupt completion is usable, ring the host interrupt register, then either wait on `mbx_intr_comp` or poll `qla2x00_poll()`. On success it copies selected inbound mailboxes. On timeout it either schedules DPC abort or calls `abort_isp()` directly when running in the DPC context.

Discovery begins with `FXDISC_GET_TGT_NODE_LIST` into `ha->gid_list`. `qlafx00_find_all_targets()` walks set bits in the target bitmap, issues `FXDISC_GET_TGT_NODE_INFO` per target id, compares WWPNs against `vha->vp_fcports`, updates changed target ids, marks stale online entries lost, and accumulates newly discovered ports. `qlafx00_configure_all_targets()` then moves new ports into `vha->vp_fcports` and updates the SCSI-visible loop state.

Normal SCSI submission enters `qlafx00_start_scsi()`. It takes `hardware_lock`, gets a handle, maps the command SG list, calculates IOCB count, verifies request-ring space against `req_q_out`, records the SRB in `req->outstanding_cmds`, builds a local FX00 command IOCB, emits continuation IOCBs as needed, writes the command to MMIO ring memory with `memcpy_toio()`, advances the ring pointer, marks DMA valid, writes `req_q_in`, and rings the FX00 request interrupt code.

Response processing is driven by `qlafx00_intr_handler()`. It loops over FX00 interrupt status bits, handles mailbox completions, AENs, and response queue completions, clears interrupt bits, and finally calls `qla2x00_handle_mbx_completion()`. `qlafx00_process_response_queue()` copies each MMIO response entry into `rsp->rsp_pkt`, advances software ring state, dispatches by entry type, and writes `rsp_q_out`.

`qlafx00_status_entry()` validates the handle and either takes the fast path through `qla2x00_process_completed_request()` for clean completions or translates FX00 completion/SCSI status combinations into Linux SCSI results. It handles residuals, underflow/overrun, check condition and sense-buffer copy, queue-full, transport-disrupted port states, aborted commands, and default errors. Extended sense spills into `rsp->status_srb` and is completed by `qlafx00_status_cont_entry()`.

Reset recovery is timer- and DPC-driven. `qlafx00_timer_routine()` samples firmware heartbeat, sets `ISP_ABORT_NEEDED` after repeated misses, watches reset-recovery AEN states until firmware restart completion, stretches timers for long firmware reset states, checks critical-temperature recovery thresholds, and resends host information when early boot produced incomplete node data. `qlafx00_abort_isp_cleanup()` blocks online state, marks FC ports lost, aborts outstanding commands with reset/no-connect status, frees IRQs, clears FX00 interrupts, and sets the appropriate FX00 recovery bit.

## State And Persistence
There is no filesystem persistence. Persistent state is driver runtime state in `scsi_qla_host_t`, `struct qla_hw_data`, request/response queues, and `ha->mr` fields defined in `qla_mr.h`.

`ha->mr` stores firmware version strings, adapter identity strings, the special unlinked FXDISC `fcport`, heartbeat counters, reset and critical-temperature timer ticks, the last AEN state, critical temperature threshold, extended-IO capability, and host-info resend state. Firmware-provided model, serial, hardware, firmware, U-Boot, FRU, and capability fields are copied from `FXDISC_GET_CONFIG_INFO`.

Queue state is split between saved original ring pointers (`ring_fx00`, `dma_fx00`, `length_fx00`) and active BAR2-backed request/response ring pointers. Outstanding SCSI/FXDISC/TMF/abort SRBs are indexed by firmware handles in `req->outstanding_cmds`.

Discovery state persists in `vha->vp_fcports`, `fc_port_t` target ids, WWNN/WWPN fields, `ha->gid_list`, `loop_state`, and `loop_down_timer`. AENs can mark individual targets lost, mark all devices lost on no-cable conditions, or request loop resync.

## Dependencies And Integration Points
The file depends on the broader `qla2xxx` core (`qla_def.h`) for host/HBA structures, SCSI and FC port abstractions, logging, DPC flags, mailbox constants, SRB helpers, ring initialization, command abortion, IRQ allocation, and BSG integration. It depends on `qla_mr.h` for FX00 IOCB and register definitions.

Kernel integration points include PCI config/resource APIs, MMIO accessors, DMA coherent allocation for FXDISC buffers, SCSI mid-layer request blocking/unblocking, FC transport event posting through `fc_host_post_event()`, UTS host data through `utsname()`, and timekeeping through `ktime_get_real_seconds()`.

Hardware integration is through FX00 control/status registers, mailbox registers, AEN mailboxes, BAR2 request/response ring memory, host-to-HBA and HBA-to-host interrupt registers, SoC reset and temperature registers, and firmware FXDISC command semantics.

## Risks And Edge Cases
Mailbox completion has complex locking and context-dependent waiting. Timeout handling can schedule DPC recovery or call abort directly; mistakes here can double-complete mailbox state, hold `hardware_lock` too long, or miss recovery after firmware hangs.

The FX00 queue rings are MMIO-backed rather than ordinary coherent allocations after `qlafx00_config_queues()`. IOCB writes use `memcpy_toio()` and explicit barriers. Reordering, using normal memory assumptions, or mishandling ring wrap can corrupt hardware queues.

`qlafx00_start_scsi()` maps SG entries while holding `hardware_lock` and must unmap only if mapping succeeded and queueing fails. Any future error path must preserve `tot_dsds` and `SRB_DMA_VALID` semantics to avoid DMA leaks or double-unmaps.

Discovery can race with loop state transitions. `qlafx00_find_all_targets()` aborts scanning if loop-down or state transition is observed and sets `LOOP_RESYNC_NEEDED`; code that ignores that bit can attach stale target ids.

Response handling treats invalid handles and invalid multi-status counts as serious firmware/driver desynchronization and schedules ISP abort. This is correct for safety but means malformed or stale responses escalate to adapter reset.

Critical-temperature recovery intentionally blocks requests and aborts commands with no-connect semantics until temperature drops below the stored threshold. Tests must account for delayed recovery through the timer routine rather than immediate reset.

## Test Signals
Build coverage should include FX00-enabled `qla2xxx` paths and catch structure layout mismatches for `cmd_type_7_fx00`, `sts_entry_fx00`, `fxdisc_entry_fx00`, and continuation entries.

Initialization tests should exercise BAR mapping failures, invalid BAR sizes, firmware AEN states (`MBA_FW_RESTART_CMPLT`, init-in-progress, system errors), mailbox register test success/failure, queue offset/length setup, and outstanding-command allocation failure.

I/O tests should cover no-data, read, write, multi-SG, continuation IOCBs, ring wrap, queue-full ring-space retry, invalid handle response, multi-status response, residual underflow/overrun, check-condition sense continuation, port logout/config-change status, TMF completion, and abort completion.

Discovery and management tests should cover config-info parsing, port-info host attribute update, target bitmap scan, target-id changes, new target attach, target detach AEN, no-cable events, host-info registration with `(none)` nodename and delayed resend, and BSG/FXDISC request and reply payload mapping.

Recovery tests should inject mailbox timeout, firmware heartbeat stall, reset-recovery AEN progression, `0xffffffff` AEN repair path, critical-temperature AEN, shutdown-request AEN, PCI channel failure, and IRQ disable/enable paths.
