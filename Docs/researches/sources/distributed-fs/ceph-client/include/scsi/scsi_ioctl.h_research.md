<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_ioctl.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_ioctl.h

## Purpose
This header defines legacy SCSI ioctl command numbers and kernel helper prototypes for SCSI ioctl dispatch, SG_IO header copying, command permission checks, and blocking ioctls during error handling.

## Important APIs, Types, And Functions
It defines basic ioctl commands such as SEND_COMMAND, TEST_UNIT_READY, START/STOP_UNIT, DOORLOCK/DOORUNLOCK, and removal-prevention constants. Under `__KERNEL__`, it defines `Scsi_Ioctl_Command`, `Scsi_Idlun`, and `Scsi_FCTargAddress`, plus `scsi_ioctl_block_when_processing_errors()`, `scsi_ioctl()`, `get_sg_io_hdr()`, `put_sg_io_hdr()`, and `scsi_cmd_allowed()`.

## Control Flow
Block or character device ioctl paths call `scsi_ioctl()`, which must gate commands based on write permission, error-processing state, and command allowlists before passing work to SCSI/SG execution. SG_IO headers are copied in/out through dedicated helpers.

## State And Persistence
No state is stored here. Structures are ABI payloads exchanged with userspace and transient kernel copies.

## Dependencies And Integration Points
It integrates SCSI block devices, sg passthrough, reset/error handling, FC target-address reporting, and userspace legacy ioctl ABI. Kernel-only declarations depend on `scsi_device`, `gendisk`, and `sg_io_hdr`.

## Risks
Legacy ioctl ABI cannot change. Passthrough command permission must prevent destructive commands without write access. Error-handler blocking must avoid returning unsafe success during recovery. User pointer copying requires compat and bounds care in implementation.

## Test Signals
Check ioctl number stability, command allow/deny matrix by open mode, SG_IO header copy round trips, reset command behavior during EH, door lock/unlock commands, and legacy IDLUN/FC address ABI layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_ioctl.h -->
