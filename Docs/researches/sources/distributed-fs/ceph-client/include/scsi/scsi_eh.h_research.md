<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_eh.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_eh.h

## Purpose
This header declares SCSI error-handler helpers for finishing recovered commands, reporting resets, blocking I/O while errors are processed, normalizing command sense, checking sense disposition, issuing ioctl resets, and temporarily replacing command contents for EH commands.

## Important APIs, Types, And Functions
Important APIs include `scsi_eh_finish_cmd()`, `scsi_eh_flush_done_q()`, `scsi_report_bus_reset()`, `scsi_report_device_reset()`, `scsi_block_when_processing_errors()`, `scsi_command_normalize_sense()`, `scsi_check_sense()`, `scsi_sense_is_deferred()`, `scsi_get_sense_info_fld()`, `scsi_ioctl_reset()`, `scsi_eh_prep_cmnd()`, and `scsi_eh_restore_cmnd()`. `struct scsi_eh_save` stores command/request state across EH preparation.

## Control Flow
EH can save a command, overwrite it with a REQUEST SENSE or reset-related command, submit it, then restore original fields. Completed EH commands are accumulated on a done queue and flushed back through normal completion. Sense analysis returns a mid-layer disposition for retry, success, fail, or other recovery actions.

## State And Persistence
EH save state is stack/transient and includes result, residual, flags, direction, underflow, CDB, data buffer, sense SG, and optional inline-encryption request fields. Reset reports update runtime device/host awareness but no durable state is defined.

## Dependencies And Integration Points
It depends on scatterlists, `scsi_cmnd.h`, and `scsi_common.h`. It integrates with SCSI host EH threads, ioctl reset handling, sense parsing, and command completion.

## Risks
Incomplete save/restore corrupts original I/O. Deferred sense detection depends on response-code bit semantics. Blocking while processing errors must avoid deadlocking device removal or runtime PM.

## Test Signals
Exercise prep/restore with normal and protection buffers, inline encryption builds, sense disposition matrix, deferred sense detection, reset reporting, ioctl reset paths, and done-queue flush ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_eh.h -->
