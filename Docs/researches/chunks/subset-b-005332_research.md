# sources/distributed-fs/ceph-client/drivers/scsi/qla2xxx/qla_init.c lines 1-9693

## Scope

This chunk covers the beginning through line 9693 of the QLogic/Marvell `qla2xxx` Fibre Channel HBA initialization file. It includes SRB lifetime helpers, asynchronous discovery/login/logout flows, task-management and abort command paths, PCI/chip/firmware initialization, ring setup, HBA and loop/fabric discovery, reset and ISP recovery, firmware image loading for legacy and FWI2 adapters, 84xx shared-chip handling, and the 81xx/82xx-style NVRAM and restart helpers. The file continues after this chunk with FCP priority and statistics/admin helpers; those later lines are outside this report.

## Purpose

`qla_init.c` is the driver-side control plane for bringing a QLogic FC adapter from PCI device state to firmware-ready, loop-ready, and remote-port-ready state. In this range it:

- Programs PCI config-space and chip reset sequences for ISP21xx/22xx/23xx/24xx/25xx/8xxx/27xx/28xx families.
- Reads persistent adapter configuration from NVRAM/VPD/flash, builds initialization control blocks, and derives runtime policy such as timeouts, WWNs, ZIO mode, topology preference, FC4 priority, EDIF behavior, and resource counts.
- Loads or validates firmware from request-firmware blobs, flash regions, ROM mailbox load paths, or golden fallback images.
- Initializes request/response/ATIO rings, outstanding SRB tables, firmware trace buffers, firmware dump buffers, and per-qpair resource limits.
- Drives discovery for private loop, fabric, and N_Port-to-N_Port topologies, including SNS/FDMI/FC4 registration and asynchronous GNL/PLOGI/PRLI/GPDB/ADISC flows.
- Handles reset/recovery paths by quiescing I/O, purging mailbox state, marking sessions lost, reinitializing firmware/rings, and resynchronizing loops and vports.

## Important APIs, Types, and State

Key adapter and queue types are `scsi_qla_host_t` for per-host or virtual-host state, `struct qla_hw_data` for physical adapter state, `struct req_que` and `struct rsp_que` for firmware rings, `struct qla_qpair` for queue-pair resources, `fc_port_t` for discovered remote FC/NVMe ports, `srb_t` and `struct srb_iocb` for asynchronous firmware work, `struct tmf_arg` for task-management requests, and `struct event_arg` for work/event completion handoff.

Important persistent or semi-persistent structures are `nvram_t`, `struct nvram_24xx`, `struct nvram_81xx`, `init_cb_t`, `struct init_cb_24xx`, `struct init_cb_81xx`, `struct active_regions`, and `struct qla27xx_image_status`. These are populated from adapter flash or firmware and then cached in `ha->nvram`, `ha->vpd`, `ha->init_cb`, `ha->ex_init_cb`, `ha->fwdt`, and identity fields such as `vha->port_name`, `vha->node_name`, `ha->model_number`, and `ha->model_desc`.

Important state fields and flags include:

- Host/link state: `vha->flags.online`, `vha->flags.init_done`, `vha->device_flags`, `vha->dpc_flags`, `loop_state`, `loop_down_timer`, `vha->d_id`, and `vha->loop_id`.
- Hardware state: `ha->chip_reset`, `ha->flags.chip_reset_done`, `ha->flags.fw_started`, `ha->flags.fw_init_done`, `ha->current_topology`, `ha->operating_mode`, `ha->switch_cap`, `ha->fw_attributes`, and firmware version/resource fields.
- Port state: `fcport->disc_state`, `fcport->fw_login_state`, `fcport->scan_state`, `fcport->flags`, `fcport->login_gen`, `fcport->rscn_gen`, `fcport->loop_id`, `fcport->d_id`, `fcport->login_retry`, `fcport->login_succ`, `fcport->logout_on_delete`, `fcport->keep_nport_handle`, and EDIF/NVMe priority fields.
- Discovery/retry flags: `LOCAL_LOOP_UPDATE`, `RSCN_UPDATE`, `LOOP_RESYNC_NEEDED`, `RELOGIN_NEEDED`, `N2N_LOGIN_NEEDED`, `N2N_LINK_RESET`, `ISP_ABORT_NEEDED`, `ISP_ABORT_RETRY`, `RESET_MARKER_NEEDED`, `REGISTER_FC4_NEEDED`, `REGISTER_FDMI_NEEDED`, and `UNLOADING`.
- Firmware resources: `req->outstanding_cmds`, `req->num_outstanding_cmds`, `ha->fwres`, `qpair->fwres`, `ha->orig_fw_iocb_count`, `ha->orig_fw_xcb_count`, `ha->cur_fw_iocb_count`, and `ha->cur_fw_xcb_count`.

The chunk uses Linux synchronization primitives heavily: spinlocks for hardware, queue, target-session, vport, and work-list state; mutexes for firmware update and optrom/dump ownership; completions for synchronous waits on async IOCBs; krefs for SRB and shared 84xx chip lifetime; atomics for loop state, RSCN generation, and pending mailbox counters; timers for SRB timeout handling.

## SRB and Async IOCB Lifecycle

`qla2x00_sp_timeout()` is the generic SRB timer callback. It invokes the SRB's `iocb->timeout()` method, drops the command kref, and detects PCI/register disconnect through `qla2x00_isp_reg_stat()`. `qla2x00_sp_free()`, `qla2xxx_rel_done_warning()`, and `qla2xxx_rel_free_warning()` support SRB cleanup and defensive diagnostics.

`qla2x00_get_async_timeout()` derives timeout in seconds/ticks from RATOV, FX00 defaults, or older initialization-control-block login timeout. All async login-style commands allocate an SRB with `qla2x00_get_sp()` or `qla2xxx_get_qpair_sp()`, set `sp->type`, `sp->name`, generation snapshots, timeout handler, and completion callback, then submit through `qla2x00_start_sp()`.

Timeout paths (`qla2x00_async_iocb_timeout()`, `qla24xx_abort_iocb_timeout()`, `qla2x00_tmf_iocb_timeout()`) remove SRBs from `req->outstanding_cmds` under the qpair lock when firmware cannot be aborted, return firmware resources with `qla_put_fw_resources()`, synthesize completion status such as `CS_TIMEOUT`, and call the SRB's completion path. Login timeouts may first attempt `qla24xx_async_abort_cmd()`.

`qla24xx_async_abort_cmd()` builds an ABTS SRB for a target SRB and can either return immediately or wait on a completion. The done callback, `qla24xx_abort_sp_done()`, handles wakeup or kref release and waits for NVMe command references when aborting NVMe SRBs. `qla24xx_async_abort_command()` is the higher-level SCSI/NVMe abort entry: it confirms the command is still outstanding, handles FXIOCB DCMD aborts specially, then calls the async abort path with wait enabled.

## Discovery and Login Control Flow

The async discovery state machine is built around small work postings and firmware IOCBs:

- `qla2x00_async_login()`, `qla2x00_async_logout()`, `qla2x00_async_prlo()`, `qla2x00_async_adisc()`, `qla24xx_async_gnl()`, `qla24xx_async_prli()`, and `qla24xx_async_gpdb()` submit PLOGI/LOGO/PRLO/ADISC/GNL/PRLI/GPDB work.
- `qla24xx_post_gnl_work()`, `qla24xx_post_prli_work()`, `qla24xx_post_gpdb_work()`, `qla_post_els_plogi_work()`, `qla24xx_post_newsess_work()`, and `qla_post_iidma_work()` wrap asynchronous work-queue event allocation and set `FCF_ASYNC_ACTIVE` where needed.
- Completion callbacks create `event_arg` instances and dispatch to event handlers such as `qla24xx_handle_plogi_done_event()`, `qla24xx_handle_prli_done_event()`, `qla24xx_handle_adisc_event()`, `qla24xx_handle_gpdb_event()`, and the internal `qla24xx_handle_gnl_done_event()`.

Generation counters are central. PLOGI/ADISC/GPDB/GNL SRBs snapshot `fcport->rscn_gen` and `fcport->login_gen` into `sp->gen1` and `sp->gen2`. Completion handlers compare the snapshot against current values and either proceed, replay RSCNs with `qla_rscn_replay()`, schedule session deletion through `qlt_schedule_sess_for_deletion()`, or set `RELOGIN_NEEDED`. This prevents stale firmware completions from registering ports after a topology or login change.

`qla24xx_async_gnl()` serializes a shared get-name-list mailbox request through `vha->gnl.sent` and `vha->gnl.fcports`. `qla24xx_async_gnl_sp_done()` marks loop IDs used in `ha->loop_id_map`, processes every queued `fcport`, creates new session work for firmware-known ports not present in `vha->vp_fcports`, and retriggers GNL if more fcports were queued while the request was outstanding.

`qla24xx_handle_gnl_done_event()` reconciles firmware name-list entries against a candidate `fcport`: it updates loop ID and port ID, detects conflicts with other sessions, derives FC4 type from FCP/NVMe PRLI phases, and branches by topology and firmware login state. Completed PRLI usually posts ADISC/GPDB, PLOGI-complete states may post PRLI or GPDB for EDIF, and unavailable states allocate a loop ID and call `qla24xx_fcport_handle_login()`.

`qla24xx_fcport_handle_login()` is the high-level login state switch. It ignores deleted or paused sessions, defers while async work is active, prevents target-only fabric-initiated login, chooses GNL/PLOGI/PRLI/GPDB/ADISC based on `disc_state`, `fw_login_state`, topology, mode, N2N WWN ordering, EDIF state, and NVMe/FCP priority, and schedules relogin when registration is still pending.

`qla24xx_handle_plogi_done_event()` and `qla24xx_handle_prli_done_event()` interpret mailbox status codes. Successful PLOGI either posts PRLI or GPDB, sets loop ID usage, and records firmware login state. `MBS_LOOP_ID_USED` and `MBS_PORT_ID_USED` paths update `loop_id_map`, clear or transfer loop IDs, and may pause one fcport behind a conflicting session. PRLI success records NVMe service parameters and posts GPDB; PRLI failure toggles NVMe-vs-FCP retry state, triggers N2N link reset, or schedules session deletion in fabric mode.

`qla24xx_handle_gpdb_event()` parses the port database, handles secure-login and EDIF authorization handoff through `qla_chk_secure_login()`, and finalizes a successful session with `__qla24xx_handle_gpdb_event()`. Finalization increments `login_gen`, sets `logout_on_delete`, bumps `vha->fcport_count` only for first success, and schedules `qla24xx_sched_upd_fcport()` for registration/update work.

## RSCN, Loop, and Fabric Discovery

`qla2x00_handle_rscn()` maps RSCN address scope to affected `fc_port_t` entries. It marks `scan_needed`, advances `vha->rscn_gen` with a write barrier, stores the generation in affected fcports, and queues delayed scan work if not already queued. EDIF/doorbell handling suppresses redundant RSCNs while a relogin is already in progress.

`qla2x00_configure_hba()` calls firmware `get_adapter_id`, derives topology (`ISP_CFG_NL`, `ISP_CFG_FL`, `ISP_CFG_N`, `ISP_CFG_F`), operating mode (`LOOP` or `P2P`), switch capability, adapter loop ID, and host N_Port ID. It updates the host map except for selected EDIF/N2N cases and schedules ISP abort on unrecoverable adapter-ID failure.

`qla2x00_configure_loop()` is the main loop/fabric reconciliation routine. It updates HBA identity when `LOCAL_LOOP_UPDATE` is set, snapshots and clears relevant dpc flags, reads link data rate and PLOGI templates, converts local-loop vs RSCN work depending on topology, calls `qla2x00_configure_local_loop()` or `qla2x00_configure_fabric()`, sets `LOOP_READY` on success, enables EDIF link-up events, and drains ATIO queue entries that arrived while offline.

`qla2x00_configure_local_loop()` reads the firmware ID list, creates or updates `fc_port_t` records from port database entries, marks missing devices lost, and posts login handling for found devices. It may reinitialize the link and set `LOOP_RESYNC_NEEDED` when a loop map indicates devices are not yet logged in. `qla2x00_configure_n2n_loop()` handles point-to-point N2N discovery and retries until a peer session exists or scan retries are exhausted.

`qla2x00_configure_fabric()` validates fabric presence through FL/F port name reads, enables RSCN receiving in target/dual mode, logs into the management server and SNS, optionally performs FDMI/FC4 registration (`RFT_ID`, `RFF_ID`, NVMe registration, `RNN_ID`, `RSNN_NN`), and then starts either async fabric scan or synchronous `qla2x00_find_all_fabric_devs()`. It registers the local NVMe HBA when needed.

`qla2x00_find_all_fabric_devs()` prefers GID_PT/GPN_ID/GNN_ID/GFPN_ID/GFF_ID name-server queries and falls back to GA_NXT scanning. It filters self ports, vports, reserved addresses, same-domain FL entries, and optionally non-FCP ports. It updates existing fcports by WWPN, handles FC ID changes, adds new fabric fcports with `FCF_LOGIN_NEEDED`, marks stale fabric devices lost, and posts login handling.

Loop ID allocation is centralized in `qla2x00_find_new_loop_id()`, `qla2x00_clear_loop_id()`, and `qla2x00_reserve_mgmt_server_loop_id()`, all backed by `ha->loop_id_map` and protected by `ha->vport_slock` where shared.

## Remote Port Registration and Online Transition

`qla2x00_alloc_fcport()` allocates an fcport plus a coherent CT SNS buffer, initializes discovery/login/session/EDIF/list/work state, and defaults it to deleted and unconfigured. `qla2x00_free_fcport()` frees the DMA buffer, clears loop IDs, flushes EDIF security-association state, removes list membership, and releases the object.

`qla2x00_update_fcport()` is the online transition. It sets `DSC_UPD_FCPORT`, resets login retry and async flags, clears deletion under `work_lock`, chooses logout behavior by topology, applies iIDMA and FCP priority, creates debugfs rport state, and then integrates with the upper layers:

- Initiator mode calls `qla2x00_reg_remote_port()`, which uses `fc_remote_port_add()` and `fc_remote_port_rolechg()`.
- Target mode calls `qlt_fc_port_added()` when target operation is not stopped.
- Dual mode does both.
- NVMe targets call `qla_nvme_register_remote()`.

The function finally sets the port state to `FCS_ONLINE`, optionally posts GPSC/GFPNID work, and sets discovery state to `DSC_LOGIN_COMPLETE`. `qla_register_fcport_fn()` wraps this as workqueue context and replays ADISC or deletion if an RSCN arrived during registration.

## Task Management and Markers

`qla2x00_async_tm_cmd()` handles LUN reset, abort task set, clear task set, clear ACA, and target-level TMF style commands. It builds a `tmf_arg`, selects `MK_SYNC_ID_LUN` or `MK_SYNC_ID`, obtains a bounded TMF slot through `qla_get_tmf()`, executes `__qla2x00_async_tm_cmd()` on the base qpair, then releases the slot with `qla_put_tmf()`.

`qla_get_tmf()` rejects duplicate TMFs for the same fcport/LUN and throttles active TMFs to `MAX_ACTIVE_TMF` using `ha->tmf_pending` and `ha->tmf_active` lists protected by `ha->tgt.sess_lock`. It aborts waiting if the fcport becomes not ready.

`__qla2x00_async_tm_cmd()` snapshots chip and login generations, submits an SRB_TM_CMD with timeout handling, waits for completion, waits for pending SCSI commands to drain, and issues a marker through `qla26xx_marker()` if the chip/login generation did not change. Markers and TMFs both use `START_SP_W_RETRIES()` to retry `qla2x00_start_sp()` on `-EAGAIN` while generation snapshots remain stable.

## Adapter Initialization and PCI/Chip Setup

`qla2x00_initialize_adapter()` resets host statistics and adapter flags, initializes loop state, configures PCI through `ha->isp_ops->pci_config`, resets the chip, validates flash info, reads reset templates for 8044, reads flash version, configures NVRAM, verifies or loads RISC firmware, initializes 84xx shared state, initializes rings for initiator/dual mode, verifies 84xx chip state, loads 8031 NIC core firmware, reads FCP priority config on 24xx/25xx, and sets driver version in firmware.

`qla2100_pci_config()`, `qla2300_pci_config()`, `qla24xx_pci_config()`, and `qla25xx_pci_config()` program PCI command bits, memory write invalidate, latency timer, PCI-X/PCIe max read request sizes, ROM disable, interrupt-disable behavior, and cached PCI attributes/chip revision. The 2300 path includes a RISC pause/FPM register probe to work around invalid MWI on certain FB revisions.

`qla2x00_reset_chip()` implements legacy chip reset by disabling interrupts, clearing PCI bus mastering, pausing/releasing RISC, resetting FPM/frame-buffer FIFOs, asserting ISP soft reset, clearing interrupts/semaphores, waiting for mailbox readiness, restoring bus mastering, and disabling parity pause. `qla24xx_reset_chip()` disables interrupts, handles a hardware-specific RISC semaphore workaround, and delegates to `qla24xx_reset_risc()`.

`qla24xx_reset_risc()` is the FWI2 RISC reset sequence. It shuts down DMA, records firmware-dump capability flags, waits for mailbox/NVRAM access completion, performs MPI reset if requested, toggles RISC reset/pause bits, checks mailbox recovery for 27xx/28xx, and re-enables interrupts for interrupt-driven adapters. `qla_chk_risc_recovery()` logs mailbox diagnostics when newer chips report reset failure.

`qla2x00_chip_diag()` and `qla24xx_chip_diag()` validate chip/mailbox operation. The legacy path checks product IDs, adjusts firmware transfer size, handles 2200A transfer limits, and runs mailbox register tests. The 24xx path primarily sets transfer size and runs mailbox tests, skipping P3P types.

## Firmware Setup, Rings, and Resource Accounting

`qla2x00_setup_chip()` handles firmware loading and execution. It chooses P3P special handling, toggles parity for older chips, synchronizes 81xx MPI settings, calls `ha->isp_ops->load_risc`, verifies checksum, executes firmware, optionally restarts for long-range SFP/BPM detection, sets ZIO threshold, configures exchange-login and exchange-offload buffers, reads firmware version, enables NPIV support, configures target NVRAM with firmware version, reads firmware resource counts, initializes IOCB/exchange limits, allocates outstanding SRB arrays, allocates firmware dump buffers, and enables FCE/EFT trace. It also enables PUREX/ELS pass-through support when RDP/SCM/EDIF features require it.

`qla2x00_alloc_outstanding_cmds()` sizes `req->outstanding_cmds` from firmware exchange/IOCB counts for FWI2 adapters or a default for older adapters, falling back to a minimum table if the preferred allocation fails.

`qla_init_iocb_limit()` and `qla_adjust_iocb_limit()` derive per-qpair and global IOCB/exchange usage limits from original firmware resource counts and number of qpairs. These limits are used later by command submission to avoid exhausting firmware resources.

`qla2x00_config_rings()` and `qla24xx_config_rings()` populate the initialization control block with DMA addresses and lengths for request/response and ATIO queues, program hardware queue pointers, configure target-mode ATIO rings, enable shadow registers/MSI-X queue routing/multiqueue metadata, pass target ring setup to `qlt_24xx_config_rings()`, and apply user-selected link speed.

`qla2x00_init_rings()` clears outstanding SRBs, resets request/response/ATIO pointers, initializes response entries, configures rings, updates firmware options, fills NPIV/MID initialization fields, records DPORT/FA-WWPN support, enforces EDIF ELS payload size, marks firmware started, and calls `qla2x00_init_firmware()` or FX00-specific initialization. On failure it marks firmware stopped.

`qla2x00_fw_ready()` polls firmware state until ready, loop-down minimum wait, or total login wait timeout. It handles FX00 delegation, 84xx verification-wait state by sending verify IOCBs, updates retry/login/RATOV counters on success, marks no-cable state on link-down timeout, and logs failure if the firmware did not become ready for reasons other than cable absence.

## NVRAM, VPD, and Image Selection

`qla2x00_nvram_config()`, `qla24xx_nvram_config()`, and `qla81xx_nvram_config()` read NVRAM/VPD from chip-specific regions, validate IDs/version/checksums, fall back to functional defaults when invalid, and copy selected NVRAM fields into the initialization control block. All three derive host WWN/node WWN, model identity, firmware options, operating mode, retry and timeout values, link-down behavior, ZIO settings, target-reset and LIP options, and serial bytes.

The 24xx/81xx paths use little-endian 32-bit checksums and `struct init_cb_24xx` or `struct init_cb_81xx`; the older 2xxx path uses byte checksum and legacy `init_cb_t`. SPARC-specific helpers can override WWNs from Open Firmware properties.

`qla81xx_nvram_config()` additionally reads 27xx/28xx active auxiliary image status through `qla28xx_get_aux_images()` and may select primary or secondary VPD/NVRAM regions. It handles T10 PI frame-payload alignment, eNode MAC defaults, extended initialization control block copy, interrupt handshaking for non-MSI-X 83xx/27xx/28xx, RIDA format 2, driver-initiated N2N login, and FC4 priority detection via `qla2xxx_get_fc4_priority()`.

`qla27xx_get_active_image()` and `qla28xx_get_aux_images()` inspect primary/secondary image-status records in flash. They validate signatures, checksums, active bits, and generation counters, then choose active global firmware or auxiliary component regions. Helper functions include `qla27xx_print_image()`, `qla27xx_check_image_status_signature()`, `qla28xx_check_aux_image_status_signature()`, `qla27xx_image_status_checksum()`, `qla27xx_compare_image_generation()`, and `qla28xx_component_status()`.

## Firmware Loading Paths

Legacy `qla2x00_load_risc()` loads 16-bit firmware from `request_firmware`, validates non-empty version words and image length, walks firmware segments from the blob metadata, byte-swaps into the request ring, and loads fragments into RISC RAM via `qla2x00_load_ram()`.

FWI2 `qla24xx_load_risc_blob()` loads 32-bit firmware from `request_firmware`, validates image header words with `qla24xx_risc_firmware_invalid()`, copies fragments into the request ring with byte swapping, calls `qla2x00_load_ram()`, and for 27xx/28xx also extracts firmware dump templates into `ha->fwdt`.

`qla24xx_load_risc_flash()` performs the same segment and optional template load from flash addresses using `qla24xx_read_flash_data()`. `qla28xx_get_srisc_addr()` and `qla28xx_load_fw_template()` support secure 28xx flash-load flows that use ROM mailbox firmware loading but still need the start RISC address and dump templates from flash.

`qla24xx_load_risc()` tries request-firmware first unless `ql2xfwloadbin == 1`, then falls back to flash. `qla81xx_load_risc()` has a broader priority order: 28xx secure ROM flash load, selected secondary or primary flash image for 27xx/28xx, primary flash for other chips, request-firmware blob, and golden flash firmware fallback. Golden fallback sets `ha->flags.running_gold_fw` and logs that a firmware flash update is needed.

`qla2x00_try_to_stop_firmware()` attempts a stop-firmware mailbox command for FWI2 adapters with loaded firmware, retrying by resetting/reloading the chip up to five times for retryable failures, then marks firmware stopped.

## Trace, Dump, and Diagnostic Buffers

`qla2x00_alloc_fce_trace()` allocates coherent FCE trace buffers for capable FWI2 adapters; `qla2x00_free_fce_trace()` releases them. `qla_enable_fce_trace()` and `qla_enable_eft_trace()` clear and re-enable firmware/extended trace buffers after initialization or restart.

`qla2x00_alloc_fw_dump()` computes firmware dump size by chip family, firmware memory size, queue sizes, multiqueue state, ATIO queue, FCE/EFT buffers, exchange offload/login buffers, and 27xx/28xx firmware dump templates. It uses `vmalloc`, protects replacement through `ha->optrom_mutex`, preserves an already captured dump when resizing, initializes dump headers for non-template dump formats, and points `ha->mpi_fw_dump` into the combined buffer for 27xx/28xx.

`qla2xxx_mctp_dump()` allocates a coherent MCTP dump buffer, captures MCTP data through firmware, marks `ha->mctp_dumped`, and on port 0 can trigger NIC firmware restart while guarding `nic_core_reset_hdlr_active`.

## Reset, Recovery, and Restart

`qla2x00_quiesce_io()` marks the loop down, marks devices lost across base and vports, and waits for pending host commands to drain. It blocks new I/O without destroying context.

`qla2x00_abort_isp_cleanup()` is the common pre-restart cleanup: it clears online state for non-P3P, clears chip-reset-done, increments abort stats, purges mailbox waiters, resets chip where applicable, saves topology, marks firmware stopped, increments `ha->chip_reset`, propagates chip generation to qpairs, waits briefly for staged mailbox commands to drain, marks devices lost across vports, clears async/login scan flags, runs P3P chip-reset cleanup, aborts all outstanding commands with `DID_RESET`, and publishes a write barrier.

`qla2x00_abort_isp()` orchestrates ISP recovery. It calls cleanup, handles isolated port and PCI offline cases, optionally skips reset for `ISP_ABORT_TO_ROM`, clears 8031 driver presence, rereads flash/NVRAM, updates per-port NVMe PRLI preference, calls `qla2x00_restart_isp()`, enables interrupts and marks online on success, or schedules bounded retries through `ISP_ABORT_RETRY` and `ha->isp_abort_cnt`. On success it reconfigures the base HBA and aborts/restarts vports; on final failure it disables the board.

`qla2x00_restart_isp()` reloads firmware if needed, initializes rings, sets chip-reset-done, initializes additional queues, waits for firmware ready, issues a global marker, and sets `LOOP_RESYNC_NEEDED`. Cable absence is treated as nonfatal after firmware-ready failure.

`qla82xx_restart_isp()` is the P3P/82xx-style restart: initialize rings, wait for firmware ready, marker, online, interrupt enable, trace re-enable, firmware-version/check-md update, and vport abort/restart. It also treats no-cable as a successful restart.

`qla2x00_loop_resync()` waits for firmware ready, issues markers, repeatedly configures devices while `LOOP_RESYNC_NEEDED` is set, and stops if ISP abort is needed, loop goes down, or retry budget expires. `qla2x00_perform_loop_resync()` sets the necessary dpc flags and loop state before invoking it.

`qla2x00_reset_adapter()` and `qla24xx_reset_adapter()` provide simpler adapter reset entry points that mark offline, disable interrupts, assert/release RISC reset/pause, and re-enable interrupts for no-polling FWI2 adapters.

## 83xx/84xx/Virtual HBA Integration

`qla83xx_nic_core_fw_load()` handles 8031 NIC core initialization under IDC lock. It sets driver presence, determines reset ownership, validates IDC major/minor versions, may set device state READY for the reset owner, and runs the IDC state handler.

`qla83xx_reset_ownership()`, `qla83xx_initiating_reset()`, `qla83xx_nic_core_reset()`, `__qla83xx_set_drv_ack()`, `__qla83xx_clear_drv_ack()`, `qla83xx_idc_audit()`, `__qla83xx_set_idc_control()`, `__qla83xx_get_idc_control()`, and `qla83xx_check_driver_presence()` coordinate multi-function NIC-core reset through IDC registers. Ownership is based on driver presence and lowest FCoE function, and reset participants acknowledge through IDC driver-ack bits.

The 84xx support block maintains a global `qla_cs84xx_list` keyed by PCI bus. `qla84xx_get_chip()` shares a `struct qla_chip_state_84xx` across functions on the same bus with krefs; `qla84xx_put_chip()` releases it; `qla84xx_init_chip()` serializes chip verification through a firmware-update mutex.

`qla24xx_configure_vhba()` configures a virtual HBA: it waits for base firmware ready, sends a marker, resets management-server login state, logs into SNS as the vport, marks loop up, sets loop resync/local update flags, and asks the base VHA to run loop resync.

## Dependencies and Integration Points

This chunk depends on local qla2xxx headers and many sibling source files:

- `qla_def.h` and `qla_gbl.h` provide core types, macros, module parameters, firmware mailbox helpers, ISP ops, and exported functions.
- `qla_target.h` and target helpers provide target/dual-mode session deletion, ATIO ring processing, NVRAM target-stage hooks, and target port-add callbacks.
- Name-server, FDMI, NVMe, EDIF, debugfs, firmware dump-template, flash, mailbox, PCI, and queue helpers are called throughout but implemented elsewhere.
- Linux SCSI FC transport integration is through `fc_remote_port_add()`, `fc_remote_port_rolechg()`, `struct fc_rport`, and host locks.
- Linux PCI and DMA APIs are used for config-space programming, coherent buffers, PCIe read-request sizing, ROM disable, and PCI channel-offline handling.
- Linux firmware loading is through `qla2x00_request_firmware()` and the request-firmware blob carried by `struct fw_blob`.

Hardware integration is mediated by `ha->isp_ops`, which supplies chip-family-specific callbacks such as `pci_config`, `reset_chip`, `chip_diag`, `load_risc`, `config_rings`, `update_fw_options`, `nvram_config`, `fabric_login`, `fabric_logout`, `read_nvram`, `read_optrom`, `get_flash_version`, `enable_intrs`, and `disable_intrs`.

## State and Persistence Behavior

The driver treats flash/NVRAM/VPD as authoritative but not trusted. Invalid checksums, IDs, or versions cause in-memory defaults to be synthesized; this permits the adapter to function but can leave WWPN/WWNN defaults that are explicitly logged as invalid. The code in this chunk does not write corrected NVRAM back; it builds runtime control blocks and state from read data.

Firmware image state is selected from request-firmware blobs, primary/secondary flash, secured ROM flash load, or golden firmware. Active image decisions for 27xx/28xx are based on image-status signatures, checksums, active bits, and generation comparison. Firmware dump templates and dump buffers persist in memory across runtime until freed elsewhere, and captured dumps can be preserved across reallocation.

Discovery state persists in in-memory fcport lists. Ports are not recreated on every scan when WWPN matches; instead loop IDs, D_IDs, FC4 types, login state, flags, and retry counters are updated. `login_gen` and `rscn_gen` form an in-memory coherence protocol that rejects stale async completions. `loop_id_map` persists allocated firmware loop IDs and must be cleared when fcports are deleted or loop IDs are invalidated.

Reset/recovery deliberately invalidates volatile firmware state: outstanding commands are aborted, firmware-started/init flags are cleared, chip generation is advanced, async flags are cleared, and sessions are marked lost. Persistent NVRAM identity and configuration are reread after abort, allowing runtime changes to FC4 priority and other adapter settings to take effect.

## Risks and Edge Cases

- Async completion ordering is fragile. A missing generation check or missed `FCF_ASYNC_SENT` clear can register stale sessions, leak retries, or stall relogin.
- `qla24xx_async_gpdb()` reposts GPDB work on failure paths after clearing active flags. This keeps discovery moving but can loop if resources or firmware state stay unavailable.
- Several firmware-template load failure paths return `QLA_SUCCESS` after clearing the template. That makes dump-template absence nonfatal but can hide diagnostics capability loss.
- The firmware loaders rely on image headers, segment counts, and firmware size metadata. Bounds checks exist in the legacy loader but the FWI2 blob path assumes the blob layout matches expected segment/template structure once the initial header looks valid.
- Loop ID ownership is shared across vports and async discovery. Incorrect locking around `ha->loop_id_map` or failure to clear IDs can exhaust loop IDs or cause login conflicts.
- `qla2x00_alloc_fcport()` contains a duplicated `ct_desc.ct_sns` failure check after the buffer is already known to exist; harmless but suggests old refactoring residue.
- TMF throttling uses sleep polling while holding list order semantics outside the lock between sleeps. It guards readiness but remains sensitive to disruption races.
- Reset paths intentionally continue through no-cable states. This is correct for link absence but can mask firmware-ready failures when cable state is misdetected.
- Many operations are gated by chip-family macros. Regression risk is high when touching shared paths such as NVRAM defaults, firmware options, ring init, or reset because behavior differs across legacy, FWI2, P3P, 27xx/28xx secure, EDIF, NVMe, target, initiator, and dual modes.
- The static `abts_cnt` in `qla24xx_reset_risc()` is shared across calls, not per-adapter. It tracks MPI reset retry exhaustion globally within the module, which can matter on multi-adapter systems.
- Several routines clear or set `vha->dpc_flags` while other delayed/workqueue paths can set them concurrently. The code often restores saved flags after resync, but race coverage depends on exact bit ownership.

## Test and Validation Signals

Useful validation points for this chunk include:

- Probe/bring-up logs showing successful PCI config, flash validation, NVRAM config, firmware load/checksum/execute, firmware version read, resource counts, ring initialization, and `F/W Ready - OK`.
- Negative bring-up tests with invalid NVRAM checksum/ID/version confirming fallback defaults, minimum login timeout, WWN handling, ZIO settings, and no crash.
- Firmware loading matrix: request-firmware success, request-firmware missing with flash fallback, 27xx/28xx primary/secondary image selection, secured 28xx ROM flash load, and golden firmware fallback.
- Loop/fabric discovery tests for NL, FL, N_Port-to-N_Port, and F_Port topologies, including GID_PT success, GA_NXT fallback, SNS login failure, RSCN storms, and no-cable timeout.
- Async discovery races: RSCN during PLOGI/ADISC/GPDB, conflicting loop ID/N_Port ID, login generation changes from target mode, GNL batching, and session deletion while async work is active.
- Mode-specific tests for initiator, target, and dual modes, verifying `fc_remote_port_add()`, `qlt_fc_port_added()`, NVMe remote registration, and target-only login suppression.
- EDIF tests for secure and non-secure login, DBELL active/inactive behavior, authentication-needed event generation, PRLI deferral, and RSCN relogin throttling.
- TMF/abort tests for abort command success/failure/timeout, duplicate TMF rejection, active TMF throttling, command drain wait, marker issuance, and generation-change marker skip.
- ISP abort and restart tests exercising mailbox purge, outstanding command abort, vport restart, retry exhaustion, PCI channel offline, isolated port, `ISP_ABORT_TO_ROM`, 82xx restart, and trace re-enable.
- Locking/lifetime checks with KASAN/KCSAN/lockdep around fcport allocation/free, GNL list splicing, session deletion, qpair outstanding command removal, 84xx shared chip krefs, and firmware dump reallocation under `optrom_mutex`.
