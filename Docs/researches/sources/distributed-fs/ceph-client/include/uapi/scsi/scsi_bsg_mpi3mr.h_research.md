# sources/distributed-fs/ceph-client/include/uapi/scsi/scsi_bsg_mpi3mr.h

## Purpose
`scsi_bsg_mpi3mr.h` defines the Broadcom MPI3MR storage-controller BSG userspace ABI. It covers driver-specific management requests, MPI passthrough requests, adapter information/reset, target inventory, persistent event log and cached log data controls, host diagnostic buffers, NVMe encapsulated requests, SCSI task management, and PEL constants.

## Important APIs, Types, and Constants
Top-level command type `enum command` distinguishes `MPI3MR_DRV_CMD` from `MPI3MR_MPT_CMD`. Driver opcodes include `MPI3MR_DRVBSG_OPCODE_ADPINFO`, `ADPRESET`, `ALLTGTDEVINFO`, `GETCHGCNT`, `LOGDATAENABLE`, `PELENABLE`, `GETLOGDATA`, `QUERY_HDB`, `REPOST_HDB`, `UPLOAD_HDB`, and `REFRESH_HDB_TRIGGERS`. Buffer type constants identify RAID management request/response, data in/out, MPI reply/error/request, and HDB trace/firmware buffer types.

Driver-management payloads include `struct mpi3_driver_info_layout`, `mpi3mr_bsg_in_adpinfo`, `mpi3mr_bsg_adp_reset`, `mpi3mr_change_count`, `mpi3mr_device_map_info`, `mpi3mr_all_tgt_info`, `mpi3mr_logdata_enable`, `mpi3mr_bsg_out_pel_enable`, `mpi3mr_logdata_entry`, `mpi3mr_bsg_in_log_data`, `mpi3mr_hdb_entry`, `mpi3mr_bsg_in_hdb_status`, `mpi3mr_bsg_out_repost_hdb`, `mpi3mr_bsg_out_upload_hdb`, and `mpi3mr_bsg_out_refresh_hdb_triggers`.

Passthrough layout is `struct mpi3mr_bsg_drv_cmd`, `mpi3mr_bsg_mptcmd`, `mpi3mr_buf_entry`, `mpi3mr_buf_entry_list`, `mpi3mr_bsg_in_reply_buf`, and top-level `struct mpi3mr_bsg_packet`. Protocol passthrough subformats include `struct mpi3_nvme_encapsulated_request`, `mpi3_nvme_encapsulated_error_reply`, `mpi3_scsi_task_mgmt_request`, and `mpi3_scsi_task_mgmt_reply`, with constants for NVMe PRP/SGL offsets, SCSI task-management task types, response codes, PEL locales/classes, and MPI3 function codes.

## Control Flow and State
Userspace submits a BSG packet identifying either a driver command or MPI passthrough. Driver commands route by opcode and return typed payloads such as adapter info, target maps, log entries, HDB status, or reset completion. MPT commands use a variable buffer-entry list to describe request, response, data-in/data-out, error, and reply buffers, then the controller firmware executes the MPI request.

NVMe encapsulated flow sends an MPI3 NVMe encapsulated request whose command tail contains an NVMe command and whose data format is selected by PRP/SGL constants. SCSI task management flow sends a task-management request with task tag/type/LUN and receives IOC status plus response data.

## State and Persistence Behavior
The ABI can observe and mutate persistent controller state: resets can disrupt adapter state, PEL enable affects event reporting, diagnostic buffers can be posted/released/uploaded, log-data enable controls cached driver log entries, and target inventory reflects persistent firmware device handles and driver target IDs. The header relies on reserved fields for forward compatibility and variable-length arrays for inventories/logs/replies.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points are the `mpi3mr` SCSI driver, Broadcom MPI3 firmware protocol, BSG/SG_IO v4 userspace tools, RAID management applications, NVMe/SCSI passthrough clients, and persistent-event-log diagnostics.

## Risks and Test Signals
Risks are very high ABI-surface complexity, little-endian firmware field handling, C bitfield layout in PCI address fields, variable-length one-element arrays that require caller-sized buffers, and commands that can reset controllers or expose raw firmware buffers. Test signals include UAPI compile tests, ioctl/BSG ABI size tests on 32-bit and 64-bit builds, mocked driver dispatch for every driver opcode, negative tests for invalid buffer types/counts/lengths, and hardware integration tests for reset, PEL, HDB upload, NVMe encapsulation, and SCSI task management.
