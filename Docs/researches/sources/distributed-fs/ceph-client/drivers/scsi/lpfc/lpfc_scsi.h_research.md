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
