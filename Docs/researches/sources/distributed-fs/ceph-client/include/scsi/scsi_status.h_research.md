<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_status.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_status.h

## Purpose
This header defines SCSI message byte codes and host-byte result codes used in packed SCSI command results.

## Important APIs, Types, And Functions
`enum scsi_msg_byte` includes command completion, extended messages, save/restore pointers, disconnect, initiator/parity errors, abort/clear/reset task management messages, queue tag messages, ACA, QAS, and old SCSI-2 aliases. `enum scsi_host_status` defines `DID_OK`, connection/bus/timeout/target/abort/parity/error/reset/interruption statuses, passthrough, soft/immediate retry, requeue, transport disrupted/failfast/marginal, and compatibility gaps.

## Control Flow
There is no executable flow. Other helpers, especially in `scsi_cmnd.h` and `scsi.h`, pack these host status values into `cmd->result` and translate protocol messages into mid-layer error categories.

## State And Persistence
No state is owned. Values are ABI-visible through SG_IO and driver result reporting.

## Dependencies And Integration Points
It includes SCSI protocol constants and is used by SCSI commands, EH, SG, transports, and low-level drivers to communicate completion or transport status.

## Risks
Changing numeric values breaks userspace and driver ABI. Some old names are aliases and should not guide new code. The unused host-status block is intentionally reserved for compatibility with userspace parsers.

## Test Signals
Validate result packing/unpacking, SG_IO host status reporting, message-to-host-byte translation, transport failfast/disrupted behavior, and preservation of alias values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_status.h -->
