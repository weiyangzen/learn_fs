# subset-b-005295 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_scsi.c

## Purpose
`lpfc_scsi.c` is the SCSI/FCP fast-path and error-recovery implementation for the Broadcom/Emulex `lpfc` Fibre Channel HBA driver. It connects Linux SCSI mid-layer requests to lpfc node discovery state, FCP command/response payloads, SLI-3 IOCBs, SLI-4 WQEs, DMA/BPL/SGL setup, T10 DIF/BlockGuard protection, VMID tagging, congestion management, task-management functions, and per-LUN OAS metadata.

The file exports the usable SCSI host templates (`lpfc_template`, `lpfc_vport_template`, and the NVMe-only `lpfc_template_nvme`) plus helper entry points used by the rest of lpfc for queue-depth rampdown, request blocking/unblocking, SLI API table setup, FCP abort/XRI cleanup, PCI reset suitability, CMF counters, and OAS LUN state.

## Important APIs, Types, And Functions
The main SCSI host integration is `lpfc_queuecommand()`, `lpfc_abort_handler()`, `lpfc_device_reset_handler()`, `lpfc_target_reset_handler()`, `lpfc_host_reset_handler()`, `lpfc_sdev_init()`, `lpfc_sdev_configure()`, and `lpfc_sdev_destroy()`, all wired into the exported host templates. `lpfc_template_nvme` intentionally rejects SCSI queueing and device setup through `lpfc_no_command()`, `lpfc_init_no_sdev()`, and `lpfc_config_no_sdev()`.

Buffer management is split by hardware generation. SLI-3 allocates `struct lpfc_io_buf` plus one DMA pool buffer in `lpfc_new_scsi_buf_s3()`, retrieves from the `lpfc_scsi_buf_list_get/put` lists in `lpfc_get_scsi_buf_s3()`, and returns through `lpfc_release_scsi_buf_s3()`. SLI-4 uses per-hardware-queue IO buffers and command/response buffers via `lpfc_get_scsi_buf_s4()` and `lpfc_release_scsi_buf_s4()`, including exchange-busy placement on `lpfc_abts_io_buf_list`.

Command preparation is abstracted through function pointers installed by `lpfc_scsi_api_table_setup()`: normal DMA paths `lpfc_scsi_prep_dma_buf_s3()` and `lpfc_scsi_prep_dma_buf_s4()`, DIF-aware paths `lpfc_bg_scsi_prep_dma_buf_s3()` and `lpfc_bg_scsi_prep_dma_buf_s4()`, command IU builders `lpfc_scsi_prep_cmnd_buf_s3()` and `lpfc_scsi_prep_cmnd_buf_s4()`, and task-management builders `lpfc_scsi_prep_task_mgmt_cmd_s3()` and `lpfc_scsi_prep_task_mgmt_cmd_s4()`. `lpfc_scsi_prep_cmnd()` fills the FCP LUN, CDB, task attribute, and command buffer for ordinary I/O.

The T10 DIF/BlockGuard logic is concentrated in `lpfc_sc_to_bg_opcodes()`, `lpfc_prot_group_type()`, `lpfc_bg_scsi_adjust_dl()`, SLI-3 BPL builders `lpfc_bg_setup_bpl()` and `lpfc_bg_setup_bpl_prot()`, SLI-4 SGL builders `lpfc_bg_setup_sgl()` and `lpfc_bg_setup_sgl_prot()`, and error decoding helpers `lpfc_parse_bg_err()` and `lpfc_calc_bg_err()`. With debugfs enabled, `lpfc_bg_err_inject()` and `lpfc_bg_err_opcodes()` mutate or remap protection fields for targeted error injection.

Completion handling is split between SLI-4 `lpfc_fcp_io_cmd_wqe_cmpl()` and IOCB-style `lpfc_scsi_cmd_iocb_cmpl()`. Both set `cmd->result`, parse FCP responses through `lpfc_handle_fcp_err()`, process DI/BlockGuard failures, unmap DMA through `lpfc_scsi_unprep_dma_buf()`, call `scsi_done()`, wake abort waiters, update timing/debug/CMF counters, and release the `lpfc_io_buf`.

Task management and recovery are built from `lpfc_send_taskmgmt()`, `lpfc_check_fcp_rsp()`, `lpfc_chk_tgt_mapped()`, and `lpfc_reset_flush_io_context()`. Abort handling sends ABTS by iotag through SLI-3 or SLI-4 abort helpers, waits on `lpfc_cmd->waitq`, and coordinates with completion via `LPFC_DRIVER_ABORTED` and `pCmd` clearing.

Other important exported helpers include `lpfc_rampdown_queue_depth()`/`lpfc_ramp_down_queue_handler()` for resource-pressure queue-depth reduction, `lpfc_scsi_dev_block()` for permanent PCI-slot failure, `lpfc_sli4_io_xri_aborted()` and `lpfc_sli4_vport_delete_fcp_xri_aborted()` for aborted FCP XRI cleanup, `lpfc_block_requests()`/`lpfc_unblock_requests()`, `lpfc_update_cmf_cmd()`/`lpfc_update_cmf_cmpl()`, `lpfc_info()`, `lpfc_poll_start_timer()`/`lpfc_poll_timeout()`, `lpfc_vmid_vport_cleanup()`, and OAS device-data routines `lpfc_create_device_data()`, `lpfc_delete_device_data()`, `__lpfc_get_device_data()`, `lpfc_find_next_oas_lun()`, `lpfc_enable_oas_lun()`, and `lpfc_disable_oas_lun()`.

## Control Flow
For ordinary SCSI I/O, the mid-layer enters `lpfc_queuecommand()`. The function resolves `struct lpfc_rport_data` from `sdev->hostdata` or `struct lpfc_device_data` when OAS/FOF is enabled, validates FC transport readiness with `fc_remote_port_chkready()`, rejects protected commands if BlockGuard support is not registered, enforces node queue-depth limits, and optionally charges CMF read bandwidth through `lpfc_update_cmf_cmd()`.

After a command passes readiness checks, `lpfc_queuecommand()` obtains an `lpfc_io_buf`, stores the SCSI command in `pCmd`, stores the remote-port and node pointers, sets `cmnd->host_scribble`, builds the FCP command IU, maps data and protection scatterlists through the appropriate normal or BlockGuard DMA prep path, optionally applies VMID app-id tagging from blk-cgroup metadata, and submits the IOCB/WQE with `lpfc_sli_issue_fcp_io()`. Submission failure unmaps DMA, adjusts per-hdwq request counters, releases the buffer, backs out CMF accounting, and returns host busy or completes the failed command depending on the failure stage.

The normal SLI-3 DMA path maps the SCSI scatterlist with `dma_map_sg()`, formats either embedded extended IOCB BDEs or a BPL after the FCP command/response BDEs, validates against `cfg_sg_seg_cnt`, sets FCP transfer length, and byte-swaps the FCP command into immediate IOCB data when needed. The normal SLI-4 path uses `scsi_dma_map()`, formats SGL data entries after FCP command/response SGEs, optionally inserts LSP entries to chain extra SGL pages when `cfg_xpsgl` is enabled, sets first-burst write lengths, and applies OAS WQE flags and priority.

The DIF paths first classify the protection operation into no-DIF-on-host or separate-DIF-buffer groups. For SLI-3 they emit PDE5/PDE6/PDE7 descriptors plus data BDEs in the BPL; for SLI-4 they emit DISEED, DIF, DATA, and LSP SGEs. The code splits protection groups at 4 KiB boundaries, advances reference tags per protection group, sets guard/reference checking bits according to SCSI protection flags, converts CRC/IP-checksum opcode pairs, adjusts the FCP data length for on-wire DIF bytes, and encodes WQE DIF mode for strip, insert, or pass-through.

Completion is interrupt/worker driven from SLI code back into `lpfc_fcp_io_cmd_wqe_cmpl()` or `lpfc_scsi_cmd_iocb_cmpl()`. These routines guard the `lpfc_io_buf` with `buf_lock`, verify `pCmd`, read CQE/IOCB status and result, restore any debug-injected DIF tuple fields, translate success, FCP response failure, fabric/node busy, local reject, remote stop, exchange busy, crypto failures, invalid RPI/link-down/no-resource cases, and DI errors into SCSI result codes, then unmap DMA and call `scsi_done()` unless the command must wait for exchange-busy clear. They also wake abort waiters, release buffers, send fabric/SCSI events, maintain per-hdwq counters, and update CMF completion latency for qualifying reads.

FCP response handling in `lpfc_handle_fcp_err()` validates response length and response info, copies sense data, applies residual underflow/overrun behavior, checks dropped-frame/read-check conditions using `fcpi_parm`, and posts queue-full, busy, check-condition, or read-check events. BlockGuard completion errors are parsed in `lpfc_parse_bg_err()`, which sets descriptor sense for guard, reference, or application tag failures and adds high-water-mark LBA information when firmware supplies it; if firmware status is ambiguous, `lpfc_calc_bg_err()` walks host protection tuples and data to infer the error class.

SCSI EH abort calls `lpfc_abort_handler()`, blocks on the FC rport, obtains the `lpfc_io_buf` from `host_scribble`, checks whether the command is still on the transmit-completion queue, marks a wait queue, issues an abort by iotag through the correct SLI helper, kicks heartbeat timeout handling, optionally polls when interrupts are disabled, and waits up to twice `devloss_tmo` for completion to clear `pCmd`. LUN and target reset handlers send FCP task-management functions through `lpfc_send_taskmgmt()` and then flush orphaned I/O contexts; target reset may issue LOGO/unregister RPI if the TMF fails. Host reset takes the adapter offline, restarts the board/chipset, brings it online, and unblocks management I/O.

Device lifecycle flow starts at `lpfc_sdev_init()`, which validates the FC rport, attaches either direct rport data or OAS `lpfc_device_data` to `sdev->hostdata`, increments `sdev_cnt`, and for SLI-3 grows the shared SCSI buffer pool within HBA queue-depth limits. `lpfc_sdev_configure()` sets the queue depth and may start FCP ring polling. `lpfc_sdev_destroy()` decrements `sdev_cnt`, marks OAS device data unavailable, frees it when no OAS enablement remains, and clears `hostdata`.

## State And Persistence
The file does not write persistent storage. Its durable-for-driver-lifetime state lives in `struct lpfc_hba`, `struct lpfc_vport`, `struct lpfc_nodelist`, `struct lpfc_io_buf`, SCSI devices, FC rports, and OAS `struct lpfc_device_data` entries allocated from `phba->device_data_mem_pool`. OAS LUN enablement and priority are runtime state in `phba->luns`; entries can outlive a `scsi_device` when `oas_enabled` is true and are deleted when disabled and unavailable.

Per-command state is carried by `struct lpfc_io_buf`: `pCmd`, `rdata`, `ndlp`, `fcp_cmnd`, `fcp_rsp`, `dma_sgl`, `seg_cnt`, `prot_seg_cnt`, `cur_iocbq`, `flags`, `status`, `result`, `timeout`, `waitq`, timing fields, hardware queue identity, and optional debug protection-data restoration fields. `cmnd->host_scribble` points back to this buffer until completion or abort cleanup, so races around `pCmd` and buffer reuse are managed with `buf_lock`, `hbalock`, ring locks, and transmit-completion queue flags.

SLI-3 buffer state is maintained in two HBA-level lists protected by `scsi_buf_list_get_lock` and `scsi_buf_list_put_lock`. SLI-4 buffer state is maintained per hardware queue; exchange-busy FCP buffers are held on `lpfc_abts_io_buf_list` until XRI abort processing or ABTS response conditions make them reusable. Queue-depth pressure state includes `phba->num_rsrc_err`, `last_rsrc_error_time`, `last_ramp_down_time`, node `cmd_pending`, node `cmd_qdepth`, and SCSI `queue_depth`.

CMF/congestion-management state is held in per-CPU `cmf_stat`, `cmf_max_bytes_per_interval`, `cmf_bw_wait`, `cmf_busy`, `cmf_stop_io`, and latency timestamps. Polling state is the `fcp_poll_timer` and `cfg_poll` bits. VMID state is in vport hash tables and associated allocations freed by `lpfc_vmid_vport_cleanup()`. BlockGuard counters such as `bg_guard_err_cnt`, `bg_reftag_err_cnt`, and `bg_apptag_err_cnt` accumulate detected integrity failures.

## Dependencies And Integration Points
This file depends on Linux PCI, DMA mapping, scatterlist, timers, spinlocks, wait queues, blk-mq, blk-cgroup FC app-id, T10 PI, CRC-T10DIF, checksum, SCSI core, SCSI EH, SCSI transport FC, and lpfc internal headers for hardware structures, SLI rings, SLI-4 queues, WQEs/CQEs, node/vport state, logging, discovery, and exported lpfc helper routines.

The primary external integration is with `struct scsi_host_template` and the SCSI mid-layer. It also integrates with FC transport through `fc_remote_port_chkready()`, `fc_block_rport()`, `fc_remote_port_delete()`, `fc_host_post_vendor_event()`, `fc_eh_timed_out()`, and `fc_eh_should_retry_cmd()`. Block-layer integration appears in `blk_mq_unique_tag()` hardware-queue selection and `blkcg_get_fc_appid()` VMID classification. Hardware submission and cleanup are delegated to lpfc SLI helpers such as `lpfc_sli_issue_fcp_io()`, `lpfc_sli_issue_iocb_wait()`, `lpfc_sli_issue_abort_iotag()`, `lpfc_sli4_issue_abort_iotag()`, `lpfc_sli_abort_taskmgmt()`, `lpfc_sli_sum_iocb()`, `lpfc_sli_handle_fast_ring_event()`, `lpfc_set_rrq_active()`, and many SLI-4 buffer/SGL allocators.

## Risks And Edge Cases
The highest-risk areas are race-prone command ownership transitions. `cmnd->host_scribble`, `lpfc_cmd->pCmd`, `LPFC_IO_ON_TXCMPLQ`, `LPFC_DRIVER_ABORTED`, `LPFC_SBUF_XBUSY`, and wait queues are shared by queueing, completion, abort, XRI-abort, and reset flows. Missed locking or premature buffer release would surface as double completion, use-after-free, stuck abort waits, or leaked exchange-busy buffers.

DMA and SGL/BPL accounting is delicate. The normal and DIF paths must keep `seg_cnt` and `prot_seg_cnt` accurate for `lpfc_scsi_unprep_dma_buf()`, must not exceed configured SGE/BDE limits unless extended chained SGLs are available, and must correctly back out both data and protection mappings on every partial failure. Several DIF builders return sentinel counts greater than limits to signal overflow, so callers must preserve those semantics.

Protection-data handling has many mode combinations: CRC versus IP checksum, read versus write, strip/insert/pass, guard/reference check flags, application-tag escape values, 4 KiB DIF boundary splitting, and first-burst length adjustments. Mistakes here can create silent data-integrity corruption or incorrect sense data. Debug error injection intentionally mutates host protection buffers and relies on completion to restore them.

FCP response and residual logic decides whether an underrun is acceptable, an overrun is fatal, or `fcpi_parm` indicates dropped frames. This logic is tied to SCSI status, sense validity, underflow thresholds, and known adapter quirks; regressions may cause false I/O failures or missed fabric data-loss detection.

Resource pressure paths reduce queue depth globally across vports and may interact with node-level `cmd_pending` queue-depth gating. CMF managed mode blocks SCSI requests when per-interval bytes exceed the configured budget and relies on later unblocking by congestion-management code outside this file.

OAS/FOF changes the meaning of `sdev->hostdata` from `lpfc_rport_data` to `lpfc_device_data`. Call sites must use `lpfc_rport_data_from_scsi_device()` when they need the rport data, or they will misinterpret hostdata. OAS device-data list operations require `devicelock` except for the internal unlocked lookup helper.

Some waits are bounded but long: abort and reset flush can wait up to twice `devloss_tmo`; target mapping waits in 500 ms intervals. Host reset is broad and disruptive. PCI reset suitability in `lpfc_check_pci_resettable()` is intentionally conservative but depends on bus enumeration assumptions.

## Test Signals
Strong validation signals include SCSI discovery on physical and virtual ports, SLI-3 and SLI-4 ordinary read/write/no-data command submission, queuecommand failure unwinding under DMA-map failure and IO-buffer exhaustion, `cmd_pending` increment/decrement balance, SLI-4 hardware-queue selection by blk-mq tag, XRI exchange-busy reuse delay and aborted-XRI cleanup, and correct behavior with FCP ring polling enabled and interrupts disabled.

Data-integrity tests should cover all supported `scsi_get_prot_op()` modes, CRC and IP-checksum guard handling, separate protection buffers, no-DIF host buffers, 4 KiB DIF SGE/PDE boundary splits, extended chained SGL exhaustion, injected guard/reference/application tag errors, firmware DI error parsing, high-water-mark sense descriptor LBA reporting, and DMA unmap balance after every DIF setup error.

Recovery tests should include SCSI abort racing with normal completion, abort timeout, device reset, target reset with successful TMF, target reset with failed TMF and LOGO fallback, host reset restart, devloss/rport-block handling, fabric busy and node busy completions, local reject invalid-RPI/link-down/no-resource paths, remote-stop RRQ activation, queue full/busy event posting, and SLI-3/SLI-4 task-management response parsing.

State-management tests should exercise OAS LUN enable, disable, find-next, `sdev_init()`/`sdev_destroy()` lifetime, FOF hostdata casting, VMID tagging from blk-cgroup app-id, CMF request blocking/unblocking accounting, queue-depth rampdown worker behavior across vports, and module unload or HBA teardown with non-empty ABTS and OAS lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_scsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_scsi.h

## Purpose
`lpfc_scsi.h` is the private SCSI/FCP protocol contract for the lpfc driver. It defines the wire-format FCP command and response payloads used by `lpfc_scsi.c`, small list convenience macros, FC transport per-rport data, OAS per-LUN identity/state structures, command/task-management constants, BlockGuard/SCSI DMA sizing constants, port-speed compatibility constants, and a small sysfs/debugfs temporary string limit.

## Important APIs, Types, And Macros
`struct lpfc_rport_data` stores the lpfc node pointer associated with an FC remote port. `struct lpfc_device_id` identifies an OAS LUN by vport WWPN, target WWPN, and LUN. `struct lpfc_device_data` is the runtime OAS LUN record linked in `phba->luns`; it carries the rport data pointer, identity, priority, `oas_enabled`, and `available` flags.

`struct fcp_rsp` models the FCP response IU: reserved words, status-validity byte, SCSI status byte, residual count, big-endian sense and response lengths, response-info code, and an embedded 128-byte sense buffer region. Its macros define response validity bits (`RSP_LEN_VALID`, `SNS_LEN_VALID`, `RESID_OVER`, `RESID_UNDER`), response info codes (`RSP_NO_FAILURE`, task-management failures, command-field errors, read-offset mismatch), and sense constants used by the SCSI path.

`struct fcp_cmnd` and `struct fcp_cmnd32` model 16-byte and 32-byte CDB FCP command IUs. Both contain an encoded `struct scsi_lun`, control bytes, CDB storage, and big-endian transfer length. `LPFC_FCP_CDB_LEN` and `LPFC_FCP_CDB_LEN_32` drive the choice between the two layouts in SLI-4 command setup and completion.

Command and task-management constants define FCP task attributes (`SIMPLE_Q`, `HEAD_OF_Q`, `ORDERED_Q`, `ACA_Q`, `UNTAGGED`), task-management function bits (`FCP_ABORT_TASK_SET`, `FCP_CLEAR_TASK_SET`, `FCP_BUS_RESET`, `FCP_LUN_RESET`, `FCP_TARGET_RESET`, `FCP_CLEAR_ACA`, `FCP_TERMINATE_TASK`), and transfer direction bits (`WRITE_DATA`, `READ_DATA`). DMA sizing constants include `LPFC_SCSI_DMA_EXT_SIZE` and `LPFC_BPL_SIZE`; `MDAC_DIRECT_CMD`, OAS search sentinels, `TXRDY_PAYLOAD_LEN`, and `LPFC_MAX_SCSI_INFO_TMP_LEN` support specialized lpfc paths.

`list_remove_head()` and `list_get_first()` are driver-local list helpers used by SCSI buffer list management and similar queues. The fallback `FC_PORTSPEED_128GBIT` and `FC_PORTSPEED_256GBIT` definitions let the driver build against kernel headers that do not yet expose newer FC speed constants.

## Control Flow
This header has no executable control flow beyond the list macros. Its definitions directly shape `lpfc_scsi.c`: queuecommand fills `struct fcp_cmnd` or `struct fcp_cmnd32`, completion reads `struct fcp_rsp`, task-management code sets `fcpCntl2` to the FCP task-management constants, and command-prep code sets `fcpCntl3` to `READ_DATA` or `WRITE_DATA`.

The response validity and residual macros drive FCP completion control flow. `lpfc_handle_fcp_err()` checks `RSP_LEN_VALID` before trusting response-info bytes, checks `SNS_LEN_VALID` before copying sense data, uses `RESID_UNDER` and `RESID_OVER` to set SCSI residuals or errors, and interprets response-info codes for task-management completion.

The OAS structures drive the alternate `sdev->hostdata` path: when `cfg_fof` is enabled, `sdev->hostdata` points to `struct lpfc_device_data` instead of directly to `struct lpfc_rport_data`; command and debug paths must dereference through the device-data record to reach the rport data and to decide whether to set OAS WQE/IOCB flags and priority.

## State And Persistence
All state described by this header is runtime kernel-driver state, not persistent on disk. `struct lpfc_device_data` entries may persist beyond an individual `scsi_device` lifetime when a LUN remains OAS-enabled; its `available` flag mirrors whether the OS currently has a matching SCSI device, while `oas_enabled` records runtime OAS policy.

FCP payload structures are per-command DMA-visible buffers. `struct fcp_rsp` is written by adapter/firmware and consumed by completion. `struct fcp_cmnd`/`fcp_cmnd32` are written by the driver before submission and consumed by firmware/target. The fields use explicit big-endian types or comments for wire-endian values, so byte-order conversion is part of the state contract.

`struct lpfc_rport_data` is attached to FC rports by the transport/lpfc discovery layer and points back to `struct lpfc_nodelist`, which is the authoritative node/session state used by SCSI command submission and recovery.

## Dependencies And Integration Points
The header includes `<asm/byteorder.h>` and relies on SCSI and lpfc types supplied by including translation units, including `struct scsi_lun`, `struct list_head`, `struct lpfc_name`, and `struct lpfc_nodelist`. It is not a UAPI header; it is private to the lpfc driver.

Its wire-format FCP definitions integrate the Linux SCSI mid-layer with Fibre Channel Protocol payloads. Its OAS structures integrate `lpfc_scsi.c` with broader lpfc configuration/state in `struct lpfc_hba`, including `phba->luns`, `phba->devicelock`, and the OAS sysfs/debug paths that enumerate or modify enabled LUNs.

## Risks And Edge Cases
The header defines both 16-byte and 32-byte CDB layouts, but only these two sizes. Any command path copying a CDB longer than `LPFC_FCP_CDB_LEN_32` into `fcp_cmnd32.fcpCdb` would overflow unless constrained elsewhere by SCSI host/device limits. The C file chooses the 32-byte structure when `cmd_len > 16`, so host limits must remain consistent with this storage.

`struct fcp_rsp` embeds 128 bytes of sense data, while the SCSI core sense buffer size can differ by kernel version. Completion clamps copied sense length to `SCSI_SENSE_BUFFERSIZE`, but firmware-provided `rspSnsLen` and `rspRspLen` must still fit the actual DMA allocation layout established in `lpfc_io_buf`.

The list macros assume the caller has appropriate locking and that removed entries are linked through the named member. Misuse would corrupt driver queues. OAS hostdata polymorphism is another sharp edge: code that casts `sdev->hostdata` directly to `lpfc_rport_data` while `cfg_fof` is enabled will read the wrong object.

The FCP response fields are documented as big-endian for residual and length values; every consumer must keep using `be32_to_cpu()`/`cpu_to_be32()` as appropriate. Mixed endian access would break residual, response length, sense length, and transfer length handling.

## Test Signals
Header-level validation should include build coverage for kernels with and without `FC_PORTSPEED_128GBIT`/`FC_PORTSPEED_256GBIT`, compile-time or runtime checks that 16-byte and 32-byte CDB commands are encoded into the correct FCP IU size, task-management constants produce expected FCP control bits, FCP response residual/sense/response-info fields parse correctly with big-endian conversions, and OAS `sdev->hostdata` lookup works both with `cfg_fof` enabled and disabled.

Useful integration tests include sense copy with `SNS_LEN_VALID`, response-info validation with `RSP_LEN_VALID`, underflow and overrun residual handling, 32-byte CDB I/O, task-management response codes (`RSP_TM_NOT_SUPPORTED`, `RSP_TM_NOT_COMPLETED`, `RSP_TM_INVALID_LU`), OAS LUN priority propagation into WQE fields, and list helper use under the locks protecting SCSI buffer get/put lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_scsi.h -->
