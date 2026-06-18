# sources/distributed-fs/ceph-client/drivers/scsi/mpi3mr/mpi/mpi30_init.h

## Purpose
`mpi30_init.h` defines the MPI 3.0 initiator I/O request and reply ABI for SCSI commands and task management in the Broadcom `mpi3mr` driver. It is the wire format used to submit SCSI I/O to firmware, describe CDB and SGL placement, request data direction and task attributes, and decode SCSI status, sense, protection-information, and task-management completion results.

## Important APIs, Types, And Functions
`struct mpi3_scsi_io_request` is the main SCSI I/O request frame. It contains host tag, function, message flags, device change count, device handle, I/O flags, skip count, data length, eight-byte LUN encoding, a CDB union, and four inline SGL entries. `union mpi3_scsi_io_cdb_union` can hold a 32-byte CDB, an EEDP32 CDB/protection-information descriptor, or a common SGE for separate CDB buffering. `struct mpi3_scsi_io_cdb_eedp32` stores a 20-byte CDB plus primary reference/application tags and transfer length.

Request flags define large-CDB placement, task attribute (`SIMPLEQ`, `HEADOFQ`, `ORDEREDQ`, `ACAQ`), command priority, data direction, host protection-information DMA operation, and divert-to-firmware reasons such as I/O throttling or oversized WRITE SAME. Message flags indicate metadata SGL validity and firmware diversion. `MPI3_SCSIIO_METASGL_INDEX` identifies the inline SGL slot used for metadata.

`struct mpi3_scsi_io_reply` carries host tag, function, IOC status/log info, SCSI status/state, device handle, transfer and sense counts, response data, task tag, status qualifier, EEDP error offset, observed application/guard/reference tags, and the sense-data buffer address. Reply flags mark which observed PI fields are valid.

The file also defines SCSI status constants, SCSI state/sense availability bits, packed response-data masks and shifts, unknown task tag value, task-management message flags, task management function types, and task management response codes.

## Control Flow
This header has no executable control flow. Driver I/O submission code fills `mpi3_scsi_io_request`, chooses CDB representation based on command length, sets data direction and task attributes from the SCSI command, maps data and optional metadata SGLs, posts the frame to firmware, then matches `host_tag` in the reply to complete the original command.

Completion code reads `mpi3_scsi_io_reply`: `ioc_status` and `ioc_log_info` describe firmware transport outcome; `scsi_status` and `scsi_state` determine SCSI result and sense handling; `transfer_count` contributes residual calculation; `sense_count` and `sense_data_buffer_address` identify sense data; task tag and response data support task-management and protocol responses; EEDP fields describe protection-information failures.

## State And Persistence
The request and reply frames are transient DMA/message-ring state shared between host and firmware. They are not persistent on disk. The only lasting effect is the completed SCSI command result or task-management recovery action. Device handles and change counts tie frames to controller-discovered device state from config pages and events.

## Dependencies And Integration Points
The header depends on endian-annotated kernel types and common MPI SGE definitions (`struct mpi3_sge_common`, `union mpi3_sge_union`). It integrates with the `mpi3mr` SCSI queuecommand path, firmware request queues, completion queues, sense-buffer management, protection-information handling, task-management/error-recovery code, and config/topology code that supplies device handles and change counts.

## Risks And Edge Cases
The request layout is firmware ABI. The driver must set flags consistently with CDB length and buffer placement; using inline CDB fields for a CDB that requires separate buffering, or failing to set `MPI3_SCSIIO_FLAGS_CDB_IN_SEPARATE_BUFFER`, can make firmware read the wrong command. Data direction, metadata SGL index, EEDP fields, and SGL counts must match mapped DMA buffers to avoid data corruption.

Completion interpretation must distinguish firmware IOC failures from target SCSI status. Sense states can report valid sense, failed sense, empty sense-buffer queue, or unavailable sense; treating all check conditions as valid sense would lose error detail or copy invalid data. PI observed tag fields are only meaningful when the corresponding reply message flag is set.

Task-management response codes include ordinary success/failure, invalid frame/LUN, overlapped tag, queued-on-IOC, and NVMe-denied cases. Error recovery should not collapse all nonzero codes into one behavior because queued or denied operations may require different retry/escalation.

## Test Signals
I/O tests should validate request frame construction for no-data, read, write, protection-information, metadata SGL, 16-byte-or-less CDB, greater-than-16 CDB, separate-CDB buffer, and diverted-to-firmware cases. Completion tests should cover good status, check condition with valid sense, busy, task set full, reservation conflict, terminated/no-status, residual calculation from `transfer_count`, EEDP observed tag reporting, and all task-management function/response mappings.
