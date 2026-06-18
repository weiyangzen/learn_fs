# subset-b-005337 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.h

## Purpose
`qla_mr.h` defines FX00 multi-role adapter constants, IOCB wire formats, firmware discovery payloads, MMIO register offsets, register access macros, mailbox/resource limits, firmware state codes, and the `struct mr_data_fx00` per-adapter runtime state used by `qla_mr.c` and the wider `qla2xxx` driver.

It is primarily an ABI contract between driver code and FX00 firmware/hardware. The structures in this file are laid out to match firmware IOCBs and discovery responses, so field sizes, endian annotations, packing, and offsets are semantically important.

## Important APIs, Types, And Functions
Core SCSI and response IOCB formats are `struct cmd_type_7_fx00`, `struct sts_entry_fx00`, `struct multi_sts_entry_fx00`, `struct tsk_mgmt_entry_fx00`, and `struct abort_iocb_entry_fx00`. These carry command handles, target ids, LUNs, CDBs, DSDs, residuals, SCSI status, sense data, TMF flags, and abort handles.

Vendor/management IOCB formats are `struct ioctl_iocb_entry_fx00`, `struct fxdisc_entry_fx00`, `struct qla_mt_iocb_rqst_fx00`, and `struct qla_mt_iocb_rsp_fx00`. They support FXDISC requests, BSG/vendor pass-through, request/response DSDs, adapter ids, sequence numbers, status words, and dataword fields.

Firmware discovery payloads include `struct qlafx00_tgt_node_info`, `struct port_info_data`, `struct host_system_info`, `struct register_host_info`, and `struct config_info_data`. These define target WWNN/WWPN state, local port identity and link parameters, Linux host identity registration, adapter model/serial/firmware strings, cluster/capability data, and nominal temperature.

Register and interrupt constants include `QLAFX00_HBA_ICNTRL_REG`, `QLAFX00_HST_RST_REG`, `QLAFX00_SOC_TEMP_REG`, `QLAFX00_HST_TO_HBA_REG`, `QLAFX00_HBA_TO_HOST_REG`, queue BAR-window offsets, `QLAFX00_INTR_MB_CMPLT`, `QLAFX00_INTR_RSP_CMPLT`, `QLAFX00_INTR_ASYNC_CMPLT`, and the FX00 AEN values for system error, temperature, link up/down, port update, and shutdown requested.

Register access macros include `QLAFX00_SET_HST_INTR()`, `QLAFX00_CLR_HST_INTR()`, `QLAFX00_RD_INTR_REG()`, `QLAFX00_CLR_INTR_REG()`, `QLAFX00_SET_HBA_SOC_REG()`, `QLAFX00_GET_HBA_SOC_REG()`, `QLAFX00_HBA_RST_REG()`, `QLAFX00_ENABLE_ICNTRL_REG()`, `QLAFX00_DISABLE_ICNTRL_REG()`, `QLAFX00_RD_REG()`, and `QLAFX00_WR_REG()`.

`struct mr_data_fx00` is the main runtime data block embedded in `struct qla_hw_data`. It stores adapter identity strings, a generic `fcport` for unassociated requests, firmware heartbeat counters, reset and critical-temperature timers, prior AEN state, critical temperature threshold, extended-IO support, and host-info resend state.

## Control Flow
The header does not execute control flow itself, but it shapes the control flow in `qla_mr.c`.

Command submission uses `cmd_type_7_fx00`: the driver fills `entry_type = FX00_COMMAND_TYPE_7`, a firmware handle, target id, timeout, DSD count, LUN, control flags, CDB, byte count, and first DSD. Additional DSDs are emitted as `CONTINUE_A64_TYPE_FX00` continuation entries.

Firmware responses use `sts_entry_fx00`, `multi_sts_entry_fx00`, and `STATUS_CONT_TYPE_FX00`. The response parser dispatches by `entry_type`, validates handles, applies completion and SCSI status fields, copies `data[32]` sense/response bytes, and uses continuation entries when sense data exceeds the first status entry.

Discovery and management requests use `fxdisc_entry_fx00`. `qlafx00_fxdisc_iocb()` chooses request and response DSDs based on `SRB_FXDISC_*` flags, sets `func_num` to one of `FXDISC_GET_CONFIG_INFO`, `FXDISC_GET_PORT_INFO`, `FXDISC_GET_TGT_NODE_INFO`, `FXDISC_GET_TGT_NODE_LIST`, `FXDISC_REG_HOST_INFO`, or `FXDISC_ABORT_IOCTL`, and optionally passes scalar request data in `dataword`.

Reset and interrupt flows use the register macros. `qla_mr.c` writes host-to-HBA interrupt codes, clears HBA-to-host interrupt status by writing inverted masks, toggles the interrupt-control enable bit, reads SoC temperature through `QLAFX00_GET_TEMPERATURE()`, and manipulates SoC reset/fabric/timer registers during warm reset.

## State And Persistence
The header defines volatile in-kernel and hardware state only. There is no on-disk persistence.

`struct mr_data_fx00` persists while the HBA object exists. Identity fields are populated from `config_info_data`, heartbeat/timer fields are updated by the timer routine, `old_aenmbx0_state` tracks reset progress, `critical_temperature` is populated from firmware config or defaults to `QLAFX00_CRITEMP_THRSHLD`, `extended_io_enabled` reflects firmware capability bit `QLAFX00_EXTENDED_IO_EN_MASK`, and `host_info_resend`/`hinfo_resend_timer_tick` defer host registration retry.

Firmware state constants `FSTATE_FX00_CONFIG_WAIT` and `FSTATE_FX00_INITIALIZED` describe transient adapter firmware states observed through mailbox commands. Ring counts, target/lun limits, default RATOV, loop-down time, heartbeat intervals, reset intervals, critical-temperature intervals, and can-queue limits provide policy values consumed by runtime code.

## Dependencies And Integration Points
The header includes `qla_dsd.h` for `struct dsd64` and relies on definitions from the broader qla2xxx headers such as `WWN_SIZE`, `MAX_CMDSZ`, `MAX_ISA_DEVICES`, `fc_port_t`, register accessors, and bit constants.

It integrates with Linux SCSI through `struct scsi_lun` embedded in command and task-management IOCBs. It integrates with the FC transport through WWNN/WWPN fields and port/link speed values consumed by host attribute updates.

The MMIO macros assume `struct qla_hw_data` has `cregbase` mapped to FX00 control registers. The command/status structures assume request/response queue entries are `REQUEST_ENTRY_SIZE`-sized and firmware interprets little-endian fields as annotated.

## Risks And Edge Cases
Many structures represent firmware ABI and are not all marked `__packed`; changing layout, alignment, or field types can break hardware communication. The explicitly packed discovery payloads must remain byte-exact.

The `fxdisc_entry_fx00` embeds one request and one response DSD as one-element arrays even though code appends continuation entries. Bounds-checking tools may misread this pattern; driver code must keep entry-count and continuation IOCB accounting correct.

The register macros perform raw MMIO writes/reads and rely on caller locking and ordering. They do not validate offsets, state, or PCI channel health.

`QLAFX00_GET_TEMPERATURE()` performs integer arithmetic on a firmware-specific bitfield. If the register is invalid or reads all ones during PCI failure, callers must avoid trusting the resulting temperature.

`host_system_info` stores fixed-length strings copied from `utsname()`. It is safe only when callers use bounded copy as `qla_mr.c` does.

## Test Signals
Compile-time checks should cover endian annotations, packed discovery structs, and all users of FX00 IOCB types. Any change to these structures should be validated by sizeof/offset review against firmware documentation or existing hardware traces.

Runtime tests should verify command, status, multi-status, TMF, abort, IOCTL, and FXDISC IOCBs are filled with expected entry types and little-endian fields. Discovery tests should validate config/port/target payload parsing and host-info registration field truncation.

Hardware/diagnostic tests should exercise interrupt-control macros, interrupt status clear semantics, temperature conversion, heartbeat/reset interval constants, extended-IO capability detection, and critical-temperature threshold defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_mr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.c

## Purpose
`qla_nvme.c` implements FC-NVMe initiator and unsolicited link-service support for the `qla2xxx` Fibre Channel driver. It registers qla2xxx HBAs and discovered FC ports with the Linux NVMe-FC transport, maps NVMe transport callbacks to qla2xxx SRBs and firmware IOCBs, builds `COMMAND_NVME` and LS4 pass-through IOCBs, handles command and link-service aborts, and routes unsolicited FC-NVMe LS requests into the NVMe-FC core.

The file is compiled around `CONFIG_NVME_FC` checks. When NVMe-FC is disabled, exported registration/delete functions return harmlessly or fail early without touching the transport.

## Important APIs, Types, And Functions
Transport registration uses `qla_nvme_register_hba()`, `qla_nvme_register_remote()`, `qla_nvme_unregister_remote_port()`, `qla_nvme_delete()`, `qla_nvme_localport_delete()`, and `qla_nvme_remoteport_delete()`. These functions create and destroy `nvme_fc_local_port` and `nvme_fc_remote_port` objects and link their `private` fields to `scsi_qla_host` and `qla_nvme_rport`.

The NVMe-FC port template is `qla_nvme_fc_transport`. It supplies callbacks for queue creation, LS request/abort, FCP I/O/abort, unsolicited LS response transmit, queue mapping, and local/remote delete notifications. It also advertises private-data sizes, queue/segment limits, DMA boundary, and default hardware queue count.

Per-request private state is `struct nvme_private`, defined in `qla_nvme.h`, and per-unsolicited-LS state is local `struct qla_nvme_unsol_ctx`. Both use `cmd_lock`, an SRB pointer, work items, and completion status fields to coordinate asynchronous completion and abort paths.

Command and LS completion functions include `qla_nvme_sp_done()`, `qla_nvme_sp_ls_done()`, `qla_nvme_sp_lsrsp_done()`, `qla_nvme_release_fcp_cmd_kref()`, `qla_nvme_release_ls_cmd_kref()`, `qla_nvme_release_lsrsp_cmd_kref()`, `qla_nvme_ls_complete()`, and `qla_nvme_lsrsp_complete()`.

Submission paths include `qla_nvme_alloc_queue()`, `qla_nvme_ls_req()`, `qla_nvme_xmt_ls_rsp()`, `qla_nvme_post_cmd()`, and `qla2x00_start_nvme_mq()`. Abort helpers are `qla_nvme_ls_abort()`, `qla_nvme_fcp_abort()`, `qla_nvme_abort_work()`, `qla_nvme_abort_set_option()`, `qla_nvme_abort_process_comp_status()`, and `qla_wait_nvme_release_cmd_kref()`.

Unsolicited LS handling is implemented by `qla2xxx_process_purls_iocb()`, `qla2xxx_process_purls_pkt()`, `qla2xxx_get_vha_from_vp_idx()`, `qla_nvme_fc_format_rjt()`, `qla_nvme_lsrjt_pt_iocb()`, and `qla_nvme_ls_reject_iocb()`.

## Control Flow
Remote registration starts when a discovered `fc_port` advertises NVMe PRLI target or discovery service parameters. `qla_nvme_register_remote()` verifies host NVMe enablement, ensures local-port registration, filters already registered or non-target/discovery ports, builds `nvme_fc_port_info` from WWNN/WWPN/PortID/dev-loss timeout, sets role bits from PRLI parameters, calls `nvme_fc_register_remoteport()`, updates devloss, stores the `fc_port` in `qla_nvme_rport`, and sets `NVME_FLAG_REGISTERED`.

Local HBA registration is serialized by `ha->vport_lock`. `qla_nvme_register_hba()` clamps module queue count `ql2xnvme_queues` to available qpairs, updates template `max_hw_queues`, fills local port name/node name/role/PortID, sets DMA boundary from the SCSI host, and calls `nvme_fc_register_localport()`. The returned local port stores `vha` in `private`.

Queue creation maps NVMe-FC queue indexes onto qla2xxx qpairs. `qla_nvme_alloc_queue()` maps admin queue and first I/O queue to index 0, returns `ha->base_qpair` when qpairs are not enabled, reuses an existing `queue_pair_map[qidx]`, or creates a new qpair with `qla2xxx_create_qpair()` and adjusts IOCB limits.

NVMe FCP I/O enters `qla_nvme_post_cmd()`. It validates the transport private pointer, qpair, `fcport`, registered state, abort-in-progress flag, and NVMe resetting flag. It maps the transport queue to a qpair, allocates a qpair SRB, initializes kref and locks, stores `nvme_private` in `sp->priv`, sets type/name/done/put callbacks, stores the transport descriptor, and calls `qla2x00_start_nvme_mq()`.

`qla2x00_start_nvme_mq()` holds the qpair lock, allocates a firmware handle and resources, checks request-ring space, detects admin async event commands, builds a `cmd_nvme` IOCB, sets direction/first-burst/EDIF/admin-async flags, fills NPORT handle, PortID, VP index, response and command IU DSDs, payload length, and data SG DSDs plus continuation entries, writes the ring doorbell, optionally processes pending responses, and returns busy on resource or ring exhaustion.

NVMe LS requests use `qla_nvme_ls_req()`, which allocates a normal SRB, stores the NVMe-FC LS request, DMA-syncs the request payload for device, and starts the SRB. Completion is deferred through work so `fd->done()` is not invoked directly from lower-level completion context.

Abort paths take `cmd_lock`, confirm the SRB still exists, acquire `cmd_kref` with `kref_get_unless_zero()`, then schedule `qla_nvme_abort_work()`. The work item skips aborts when firmware is stopped or the session is deleted, completes locally during host shutdown, otherwise calls `ha->isp_ops->abort_command(sp)`. If ABTS-wait mode is active and firmware will complete abort asynchronously, the kref is left for abort completion; otherwise the kref is dropped before leaving the work item.

Unsolicited PURLS/LS4 responses enter through `qla2xxx_process_purls_iocb()`. The code maps VP index to a VHA, extracts source/destination IDs and opcode, finds the `fc_port`, copies possibly multi-packet payload into a `purex_item`, allocates `qla_nvme_unsol_ctx`, links it to the FC port unsolicited context list, and queues processing. `qla2xxx_process_purls_pkt()` calls `nvme_fc_rcv_ls_req()`. If the NVMe-FC core rejects it or resources are missing, the driver emits either an LS reject or exchange terminate IOCB and frees the context.

## State And Persistence
There is no on-disk persistence. State lives in the NVMe-FC transport objects, qla2xxx host/port structures, SRBs, and per-request private data.

`vha->nvme_local_port` persists while the local NVMe-FC port is registered. Each `fc_port` may hold `nvme_remote_port`, NVMe PRLI service parameters, `nvme_flag` bits (`REGISTERED`, `RESETTING`, `DELETING`), `nvme_first_burst_size`, dev-loss timeout, and an unsolicited context list.

`struct nvme_private` is transport-allocated per LS or FCP request. It tracks the in-flight SRB, transport descriptor, scheduled LS/abort work, completion status, and a spinlock that serializes completion against abort.

`struct qla_nvme_unsol_ctx` persists from unsolicited LS receipt until the response is completed or the exchange is rejected/terminated. It stores VHA, FC port, SRB, response descriptor, exchange address, NPORT handle, OX_ID, completion status, work items, and list linkage.

Active admin async-event commands increment `ha->nvme_active_aen_cnt` and avoid normal command-count accounting because they can have long timeouts.

## Dependencies And Integration Points
The file depends on Linux NVMe-FC transport APIs (`nvme_fc_register_localport()`, `nvme_fc_register_remoteport()`, `nvme_fc_unregister_*()`, `nvme_fc_rcv_ls_req()`, `nvme_fc_set_remoteport_devloss()`), block multiqueue mapping (`blk_mq_map_hw_queues()`), scatterlists, DMA sync helpers, workqueues, krefs, and NVMe command opcodes/status constants.

It integrates with qla2xxx SRB allocation and submission helpers (`qla2x00_get_sp()`, `qla2xxx_get_qpair_sp()`, `qla2x00_start_sp()`, `qla2xxx_rel_qpair_sp()`, `qla24xx_calc_iocbs()`, `qla_get_fw_resources()`, `qla_put_fw_resources()`, qpair maps, response processing, purex copy/queue helpers, and firmware abort ops).

It shares FC session state through `fc_port_t`, VP lookup via `ha->vp_list`, PortID lookup via `qla2x00_find_fcport_by_nportid()`, EDIF flags, PRLI service parameter bits, and DPC/PCI flags.

## Risks And Edge Cases
Completion and abort race handling depends on `cmd_lock`, `priv->sp`/`uctx->sp`, and `cmd_kref`. Any path that drops the last kref before clearing private pointers can use-after-free the SRB; any path that forgets the abort-acquired kref can leak SRBs.

`qla2x00_start_nvme_mq()` reserves firmware IOCB and exchange resources after acquiring a handle. On all queueing errors it must release firmware resources and avoid leaving `outstanding_cmds[handle]` visible incorrectly.

Queue index handling decrements nonzero NVMe queue indexes before lookup. Boundary checks against `max_hw_queues` and `queue_pair_map` must stay aligned with how the NVMe-FC core numbers queues.

Unsolicited LS handling assumes a registered remote NVMe port exists for the source FC port. If `fcport->nvme_remote_port` is NULL or races with delete, dereferencing `rport->private` is risky unless higher-level session teardown prevents delivery.

LS reject/terminate fallback allocates IOCBs directly from a qpair. If allocation fails, the original exchange may remain pending in firmware. Error paths free `uctx` and purex items differently depending on where failure occurred, so memory ownership must remain explicit.

First-burst, EDIF, admin async-event, and ABTS-wait options are conditional on flags and PRLI bits. These paths need focused tests because they change firmware control flags and completion accounting.

## Test Signals
Build tests should cover both `CONFIG_NVME_FC=y` and disabled configurations. Disabled builds should confirm registration/delete functions return without dereferencing NVMe transport objects.

Registration tests should cover queue-count clamping, local-port race under `vport_lock`, remote-port role bit construction, discovery-only and target roles, duplicate remote registration, devloss update, and unregister completions.

I/O tests should cover read, write, no-data/admin, admin async event, large SG lists requiring continuation IOCBs, ring full, firmware resource exhaustion, qpair mapping, first-burst enabled/disabled, EDIF-enabled transfers, and response queue opportunistic processing.

Abort tests should cover LS abort, FCP abort, host shutdown, stopped firmware, deleted sessions, async TMF enabled, ABTS wait enabled, and abort completion statuses handled by `qla_nvme_abort_process_comp_status()`.

Unsolicited LS tests should cover valid PURLS, invalid VP index, missing FC port, multi-packet copy failure, allocation failure, NVMe-FC core rejection, LS reject formatting, exchange terminate, context list add/delete, and completion of `xmt_ls_rsp()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.h

## Purpose
`qla_nvme.h` defines the qla2xxx FC-NVMe private structures, firmware IOCB layouts, constants, and public prototypes used by `qla_nvme.c` and other qla2xxx files that submit or complete NVMe-FC commands and link-service exchanges.

It forms the interface between the Linux NVMe-FC transport, qla2xxx SRB machinery, and QLogic firmware IOCB formats for `COMMAND_NVME`, LS4 request, and unsolicited LS4 receive entries.

## Important APIs, Types, And Functions
Queue constants include `MIN_NVME_HW_QUEUES`, `DEF_NVME_HW_QUEUES`, `Q2T_NVME_NUM_TAGS`, and `QLA_MAX_FC_SEGMENTS`. PURLS retry policy is described by `PURLS_MSLEEP_INTERVAL` and `PURLS_RETRY_COUNT`.

`struct nvme_private` is per-NVMe-FC request state. It stores the qla2xxx SRB pointer, LS request descriptor, scheduled LS completion work, scheduled abort work, completion status, and a spinlock used to coordinate abort and completion.

`struct qla_nvme_rport` is private data attached to an `nvme_fc_remote_port`. It points back to the qla2xxx `fc_port` and may reference an unsolicited LS context.

`struct cmd_nvme` defines the firmware FC-NVMe command IOCB. It includes a handle, NPORT handle, timeout, DSD count, response DSD length/address, command IU DSD length/address, byte count, destination PortID, VP index, first payload DSD, and control flags such as `CF_READ_DATA`, `CF_WRITE_DATA`, `CF_DATA_SEG_DESCR_ENABLE`, `CF_DIF_SEG_DESCR_ENABLE`, `CF_NVME_FIRST_BURST_ENABLE`, and `CF_ADMIN_ASYNC_EVENT`.

`struct pt_ls4_request` defines the firmware pass-through LS4 request IOCB used for outgoing NVMe LS requests, LS responses, LS rejects, and exchange termination. It carries status, NPORT handle, TX/RX DSD counts, VP index, timeout, responder/originator control flags, exchange address, byte counts, and two DSD slots.

`struct pt_ls4_rx_unsol` defines unsolicited received FC-NVMe LS entries. It carries VP index, NPORT handle, frame size, exchange address, destination/source IDs, FC header fields, OX/RX IDs, a descriptor, and the first payload words.

Exported prototypes include `qla_nvme_register_hba()`, `qla_nvme_register_remote()`, `qla_nvme_delete()`, `qla24xx_nvme_ls4_iocb()`, and `qla24xx_async_gffid_sp_done()`.

## Control Flow
The header does not execute logic, but its data layouts drive the `qla_nvme.c` flows.

For FCP I/O, `qla2x00_start_nvme_mq()` fills `cmd_nvme`: it marks `entry_type = COMMAND_NVME`, stores a qla2xxx handle, sets control flags from NVMe-FC direction, first-burst, EDIF, and admin async-event state, writes NPORT/PortID/VP routing, points firmware at the NVMe command IU and response IU DMA addresses, then appends payload DSDs.

For LS requests and responses, qla2xxx code fills `pt_ls4_request`: originator requests use TX and RX buffers from the transport LS request, responder replies use the unsolicited exchange address and TX response buffer, reject IOCBs use a locally formatted FC-NVMe LS reject buffer, and terminate IOCBs set responder-terminate control flags with no payload.

For unsolicited LS receive, response queue handling provides a `pt_ls4_rx_unsol` to `qla2xxx_process_purls_iocb()`, which uses VP index for virtual host lookup, source ID for `fc_port` lookup, exchange and OX_ID for later response, and payload offset/first-packet length constants for purex payload assembly.

## State And Persistence
There is no persistent storage. `struct nvme_private` and `struct qla_nvme_rport` are transport-private runtime allocations. Firmware IOCB structures are transient request/response ring entries.

`nvme_private.sp` is cleared under lock during completion. `qla_nvme_rport.fcport` links transport remote ports back to qla2xxx FC sessions for as long as the remote port remains registered. The unsolicited context forward declaration allows the remote-port private object to point at an active unsolicited LS exchange.

The constants in this header encode stable firmware/transport constraints, such as default queue count, first LS payload offset, number of target tags, and maximum FC segments.

## Dependencies And Integration Points
The header includes FC protocol UAPI headers, `linux/nvme-fc-driver.h`, `qla_def.h`, and `qla_dsd.h`. It therefore depends on Linux FC ELS/FS types, NVMe-FC transport request structures, qla2xxx host/port/SRB types, and qla2xxx DSD definitions.

It is consumed by `qla_nvme.c` and by other qla2xxx source files that need to build LS4 IOCBs or finish asynchronous GFF_ID work. Firmware consumes the binary layouts of `cmd_nvme`, `pt_ls4_request`, and `pt_ls4_rx_unsol`.

## Risks And Edge Cases
The firmware IOCB layouts are ABI-sensitive. Field movement, widening, signedness changes, or removing `__packed` on unaligned 64-bit fields can break DMA descriptors.

Control flag bit definitions overlap with firmware semantics. Setting both read and write, missing first-burst constraints, or using responder/originator LS4 control flag shifts incorrectly can cause firmware rejection or protocol errors.

The unsolicited receive payload only carries the first payload words in the IOCB; callers must use the defined offset/first-packet length and purex copy helpers for larger frames rather than assuming the embedded payload is complete.

`QLA_MAX_FC_SEGMENTS` and template segment limits must remain consistent with transport-advertised limits and firmware IOCB/continuation capacity.

## Test Signals
Build and static-layout review should validate `cmd_nvme`, `pt_ls4_request`, and `pt_ls4_rx_unsol` sizes and endian annotations against firmware expectations.

Runtime tests should verify command IOCBs for read/write/no-data/admin async event, LS4 originator and responder IOCBs, reject and terminate control flags, VP/PortID/NPORT routing fields, response and command IU DMA addresses, and continuation DSD behavior.

Unsolicited LS tests should assert correct extraction of opcode, source/destination IDs, exchange address, OX/RX IDs, and first payload handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nvme.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.c

## Purpose
`qla_nx.c` implements QLogic ISP82xx/8xxx "NX" adapter support for the `qla2xxx` driver. It covers CRB and memory-window address translation, PCI/IO-space setup, flash/ROM access, firmware loading from flash or firmware blobs, IDC multi-function coordination, interrupt handling, reset and quiesce state machines, watchdog health checks, option ROM read/write, doorbell IOCB start, FCoE context reset, chip-reset cleanup, minidump template execution, LED beacon control, and explicit firmware dump triggering.

This file is the shared low-level control and recovery layer for 82xx-class adapters, with some dispatch to 8044/83xx helpers when the hardware type differs.

## Important APIs, Types, And Functions
Address translation and register access are built around `qla82xx_crb_addr_transform_setup()`, `qla82xx_pci_get_crb_addr_2M()`, `qla82xx_pci_set_crbwindow_2M()`, `qla82xx_crb_win_lock()`, `qla82xx_wr_32()`, `qla82xx_rd_32()`, `qla82xx_pci_set_window()`, `qla82xx_pci_mem_read_2M()`, `qla82xx_pci_mem_write_2M()`, direct memory read/write fallbacks, and the static CRB mapping tables.

Inter-driver coordination uses `qla82xx_idc_lock()`, `qla82xx_idc_unlock()`, `qla82xx_set_drv_active()`, `qla82xx_clear_drv_active()`, `qla82xx_set_idc_version()`, reset/quiesce ready helpers, and device-state strings from `qdev_state()`.

Firmware and flash paths include `qla82xx_rom_lock()`, `qla82xx_rom_unlock()`, `qla82xx_rom_fast_read()`, `qla82xx_flash_set_write_enable()`, `qla82xx_flash_wait_write_finish()`, `qla82xx_write_flash_dword()`, `qla82xx_pinit_from_rom()`, `qla82xx_fw_load_from_flash()`, `qla82xx_fw_load_from_blob()`, URI descriptor helpers, `qla82xx_validate_firmware_blob()`, `qla82xx_load_fw()`, and `qla82xx_start_firmware()`.

Lifecycle and PCI setup are provided by `qla82xx_iospace_config()`, `qla82xx_pci_config()`, `qla82xx_reset_chip()`, `qla82xx_config_rings()`, `qla82xx_init_flags()`, `qla82xx_load_risc()`, `qla82xx_abort_isp()`, `qla82xx_fcoe_ctx_reset()`, `qla82xx_chip_reset_cleanup()`, and `qla2x00_wait_for_fcoe_ctx_reset()`.

Interrupt handling includes `qla82xx_mbx_completion()`, `qla82xx_intr_handler()`, `qla82xx_msix_default()`, `qla82xx_msix_rsp_q()`, `qla82xx_poll()`, `qla82xx_enable_intrs()`, and `qla82xx_disable_intrs()`.

Recovery and watchdog functions include `qla82xx_device_state_handler()`, `qla82xx_device_bootstrap()`, `qla82xx_need_reset_handler()`, `qla82xx_need_qsnt_handler()`, `qla8xxx_dev_failed_handler()`, `qla82xx_check_md_needed()`, `qla82xx_check_fw_alive()`, `qla82xx_check_temp()`, `qla82xx_read_temperature()`, `qla82xx_clear_pending_mbx()`, `qla82xx_watchdog()`, and `qla82xx_set_reset_owner()`.

Option ROM and minidump support is implemented by `qla82xx_read_optrom_data()`, `qla82xx_write_optrom_data()`, `qla82xx_read_flash_data()`, flash protect/unprotect/erase helpers, `qla82xx_validate_template_chksum()`, `qla82xx_md_collect()`, minidump entry processors, `qla82xx_md_alloc()`, `qla82xx_md_free()`, `qla82xx_md_prep()`, `qla82xx_beacon_on()`, `qla82xx_beacon_off()`, and `qla82xx_fw_dump()`.

## Control Flow
Initialization starts with `qla82xx_init_flags()`, which initializes the NX hardware lock, memory windows, port number, and legacy interrupt register set. `qla82xx_iospace_config()` requests PCI regions, maps BAR0 as `nx_pcibase`, assigns `iobase` based on chip type, maps or selects the doorbell write/read pointers, and limits the adapter to one request and response queue.

Firmware startup is coordinated by `qla82xx_load_risc()`, which routes 82xx hardware into `qla82xx_device_state_handler()` and 8044 hardware into 8044-specific handlers. The 82xx handler takes the IDC lock, marks this function active on first initialization, records IDC version, reads `QLA82XX_CRB_DEV_STATE`, and loops until the device becomes ready or fails. State `DEV_COLD` triggers `qla82xx_device_bootstrap()`, `DEV_INITIALIZING` sleeps and retries, `DEV_NEED_RESET` invokes reset coordination, `DEV_NEED_QUIESCENT` invokes quiesce coordination, `DEV_FAILED` disables the board, and `DEV_READY` releases the lock successfully.

`qla82xx_device_bootstrap()` decides whether firmware reset/start is needed by checking reset ownership and the PEG alive counter. If firmware must be started, it writes `DEV_INITIALIZING`, drops IDC lock while `qla82xx_start_firmware()` runs, then reacquires the lock and writes `DEV_READY` on success or `DEV_FAILED` on failure. `qla82xx_start_firmware()` scrubs DMA shift and PEG state registers, calls `qla82xx_load_fw()`, then waits for command and receive PEG state handshakes.

Firmware loading first runs `qla82xx_pinit_from_rom()`, which halts hardware engines and PEGs, applies a software reset, reads CRB initialization address/value pairs from flash, translates CRB addresses, skips protected or inappropriate registers, writes initialization values with required delays, and clears PEG state. `qla82xx_load_fw()` then prefers firmware from flash unless module policy forces blob loading. Blob loading validates either legacy flash-ROM-image magic or unified ROM image product tables, copies bootloader and firmware image data into adapter memory through 2M memory writes, writes a magic ready marker, and releases firmware from reset.

Register access is layered. `qla82xx_rd_32()` and `qla82xx_wr_32()` translate CRB addresses into direct 2M mappings when possible or take the CRB window lock and program `CRB_WINDOW_2M` for indirect access. Memory reads/writes choose MIU test-agent access for DDR/QDR ranges when possible and fall back to direct PCI memory window mapping for OCM or unusual sizes/ranges.

Interrupt handling either checks legacy interrupt vector/state registers or runs directly for MSI-X. It clears target interrupt status, reads host interrupt/status registers, dispatches mailbox completion, asynchronous event, or response queue work, clears `host_int`, invokes mailbox completion handling, and unmasks legacy interrupts when needed. The MSI-X response queue handler directly processes `qla24xx_process_response_queue()`.

Reset flow starts with `qla82xx_abort_isp()`. It marks NIC-core reset handler active, takes IDC lock, sets reset owner/device state, runs the device-state handler, clears reset-ready, and restarts the ISP on success. On failure, it uses retry counters and `ISP_ABORT_RETRY` to either schedule another attempt or disable the board through `reset_adapter()`.

The watchdog samples device state, temperature, and firmware heartbeat. Temperature panic sets unrecoverable state and clears pending mailbox commands. `DEV_NEED_RESET`, `DEV_NEED_QUIESCENT`, and `DEV_FAILED` set DPC flags. Stalled heartbeat triggers register dumps, optional unrecoverable classification from halt status, firmware-hung state, and premature mailbox completion.

Minidump collection validates the firmware-provided template checksum, checks capture mask levels, stores driver info, walks each template entry, skips entries outside the driver capture mask, executes control/read/cache/queue/ROM/memory entry processors, verifies the collected byte count, marks `ha->fw_dumped`, and posts a firmware-dump uevent.

## State And Persistence
There is no driver-owned filesystem persistence. Persistent runtime state lives in `struct qla_hw_data`, hardware CRB/flash registers, firmware state registers, and allocated firmware/minidump buffers.

Address-window state includes `ha->crb_win`, `ha->qdr_sn_window`, `ha->ddr_mn_window`, `ha->curr_window`, `ha->mn_win_crb`, `ha->ms_win_crb`, `ha->nx_pcibase`, `ha->iobase`, and doorbell pointers. The CRB transform table is static global state initialized once.

IDC and recovery state is stored in hardware registers such as `QLA82XX_CRB_DRV_ACTIVE`, `QLA82XX_CRB_DRV_STATE`, `QLA82XX_CRB_DEV_STATE`, and driver flags such as `nic_core_reset_owner`, `nic_core_reset_hdlr_active`, `quiesce_owner`, `isp82xx_fw_hung`, `isp82xx_no_md_cap`, `DFLG_DEV_FAILED`, and DPC flags.

Firmware blob state is held in `ha->hablob`, `ha->fw_type`, `ha->file_prd_off`, flash region offsets, and firmware version fields. Minidump state uses `ha->md_tmplt_hdr`, `ha->md_tmplt_hdr_dma`, `ha->md_template_size`, `ha->md_dump`, `ha->md_dump_size`, `ha->fw_dumped`, and `ha->prev_minidump_failed`.

Flash writes modify adapter option ROM persistently. `qla82xx_write_optrom_data()` unprotects flash, erases sectors, writes dwords, and reprotects flash, so that path has real device persistence even though the driver does not write host files.

## Dependencies And Integration Points
The file depends on `qla_def.h` for qla2xxx host/HBA definitions, hardware constants, logging, mailbox/DPC flags, firmware request helpers, minidump types, and 8044/83xx helper prototypes. It depends on PCI APIs, MMIO accessors including 64-bit non-atomic helpers, delays, ratelimit logging, vmalloc/vfree, SCSI request blocking, and firmware blob APIs through qla2xxx request wrappers.

It integrates with qla2xxx common firmware paths (`qla2x00_request_firmware()`, `qla2x00_get_fw_version()`, `qla2x00_abort_isp_cleanup()`, `qla82xx_restart_isp()`, `qla2x00_try_to_stop_firmware()`, `qla2x00_wait_for_chip_reset()`, `qla24xx_process_response_queue()`, `qla2x00_async_event()`, mailbox completion handling, and minidump template fetch functions).

It coordinates with other PCI functions and possibly other drivers through IDC hardware semaphores and shared CRB state registers. Correct operation requires all functions to honor `DRV_ACTIVE`, `DRV_STATE`, `DEV_STATE`, reset-ready, and quiesce-ready protocols.

## Risks And Edge Cases
CRB and memory window programming is lock-sensitive. Indirect CRB accesses take both `ha->hw_lock` and hardware semaphore 7; memory-window accesses manipulate shared window registers. Missing locks or using the wrong accessor can send reads/writes to the wrong hardware region.

Several low-level functions use `BUG_ON()` for invalid CRB translations. Bad offsets from new callers can panic the kernel rather than returning an error.

Firmware loading crosses persistent flash, firmware blob parsing, memory-window writes, and hardware reset sequencing. Partial blob validation, endian mistakes, or skipped CRB writes can leave the device in `DEV_FAILED` or a state that requires host reset.

IDC state-machine logic relies on all active PCI functions acknowledging reset or quiesce bits. Timeouts intentionally force state transitions in some paths, but that can race with another function still completing I/O.

Flash update paths persist changes to adapter ROM. Sector erase/write failures, wrong `fdt_block_size`, or interrupted updates can corrupt option ROM contents. Although flash is reprotected afterward, failures during unprotected windows matter.

Watchdog and reset paths can prematurely complete mailbox commands when firmware is hung. That avoids indefinite waits, but callers must be prepared for mailbox completion without real firmware response.

Minidump execution interprets firmware-provided templates as command streams that read/write registers and poll hardware. Bad templates, wrong capture masks, insufficient dump sizing, or access timeouts can fail collection or skip entries. The code validates checksums and total size but still performs hardware operations from template contents.

## Test Signals
Build coverage should include 82xx and 8044 configurations, MSI-X and legacy interrupt paths, firmware blob support, and minidump support.

Initialization tests should cover PCI region request/map failures, doorbell mapping modes, CRB direct and indirect access, memory reads/writes across supported sizes and boundary conditions, IDC lock timeout, active-driver register initialization from `0xffffffff`, and device states `READY`, `COLD`, `INITIALIZING`, `NEED_RESET`, `NEED_QUIESCENT`, `QUIESCENT`, and `FAILED`.

Firmware tests should exercise flash load success/failure, forced blob load, legacy blob validation, unified ROM image product-table selection, bootloader/firmware copy failure, command and receive PEG handshake timeout, and firmware version change triggering minidump resource reallocation.

Interrupt tests should cover legacy interrupt filter/unmask, MSI-X default and response handlers, mailbox completion, async events, response queue dispatch, host interrupt clearing, and PCI disconnect reads.

Recovery tests should inject watchdog heartbeat stalls, temperature warning/panic, halt status unrecoverable bits, device need-reset/need-quiescent states, reset acknowledgment timeout, quiesce timeout, abort retry exhaustion, FCoE context reset, and chip-reset cleanup with and without firmware hung.

Flash/minidump tests should cover optrom read/write sector boundaries, flash unprotect/protect failures, erase failure, dword write failure, minidump checksum failure, capture mask filtering, control opcode polling timeout, RDCRB/RDMEM/RDROM/cache/queue entries, dump-size mismatch, duplicate dump prevention, and forced dump without minidump capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_nx.c -->
