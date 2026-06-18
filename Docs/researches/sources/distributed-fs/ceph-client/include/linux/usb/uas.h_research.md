# sources/distributed-fs/ceph-client/include/linux/usb/uas.h

## Purpose
This header defines USB Attached SCSI protocol wire structures, information unit IDs, task management codes, response codes, and pipe usage descriptors.

## Important APIs, types, and functions
Important packed structures are `iu`, `command_iu`, `task_mgmt_iu`, `sense_iu`, `response_iu`, and `usb_pipe_usage_descriptor`. Enums define IU identifiers, task management functions, service response values, and endpoint usage values.

## Control flow, state, and persistence
UAS host drivers build command and task-management IUs from SCSI commands, submit them over bulk streams, and parse sense/response IUs when devices complete work. The header only describes USB wire layout; queueing state is in the UAS driver and SCSI midlayer.

## Dependencies and integration points
It depends on SCSI command and SCSI constants. It integrates USB storage transports with the Linux SCSI midlayer and endpoint/stream selection during probe.

## Risks and test signals
Risks include packed layout drift, wrong big-endian fields, tag/task attribute mismatches, and incorrect endpoint usage discovery. Tests should cover structure sizes, command IU encoding, sense parsing, task management response handling, and malformed descriptor rejection.
