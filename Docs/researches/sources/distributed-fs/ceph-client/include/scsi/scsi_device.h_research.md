<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_device.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_device.h

## Purpose
This header defines SCSI device and target objects, device state machines, events, VPD storage, queue-depth/blocking behavior, scan helpers, device-handler integration, internal command execution arguments, and many inline state/feature accessors.

## Important APIs, Types, And Functions
Core types are `struct scsi_mode_data`, `enum scsi_device_state`, `enum scsi_scan_mode`, `enum scsi_device_event`, `struct scsi_event`, `struct scsi_vpd`, `struct scsi_device`, `enum scsi_target_state`, `struct scsi_target`, `struct scsi_failure`, `struct scsi_failures`, and `struct scsi_exec_args`. APIs cover add/remove/get/put/lookup/iterate, target iteration, queue-depth changes/tracking, mode sense/select, TEST UNIT READY, VPD/opcode reports, state transitions, event allocation/send, quiesce/resume, scan/remove target, block/unblock, execute internal commands, internal command allocation, disk event disable/enable, VPD ID extraction, and runtime PM helpers.

## Control Flow
Devices are created in `SDEV_CREATED`, probed/configured, moved to `SDEV_RUNNING`, and later blocked, quiesced, offlined, canceled, or deleted through validated state transitions. Queue-full handling updates depth and blocking counters. Events are queued into `event_list` and processed by work. Internal commands use `scsi_execute_cmd()` with explicit retries, timeouts, sense, flags, and failure rules.

## State And Persistence
`struct scsi_device` stores host/queue links, target identity, inquiry/VPD data, black-list flags, feature quirks, power-management policy bits, queue accounting, event bitmaps, counters, sysfs devices, request SG settings, handler state, and aligned private data. `struct scsi_target` stores per-target lists, blocking/busy counters, target state, and transport private data.

## Dependencies And Integration Points
It depends on list/spinlock/workqueue/blk-mq/sbitmap/atomic primitives and SCSI core headers. It is a central integration point for SCSI hosts, upper-level drivers, device handlers, sysfs, VPD, runtime PM, block queues, and transport classes.

## Risks
State transitions are constrained by `scsi_device_set_state()`; bypassing them risks commands on deleted/offline devices. Many single-bit quirks encode compatibility behavior from `scsi_devinfo.h`; regressions can break old devices. VPD pointers are RCU-managed. Queue-depth ramping and blocking counters are concurrency-sensitive.

## Test Signals
Cover add/remove/get/put lifetimes, state transition acceptance/rejection, queue-full depth changes, target iteration locking variants, event delivery, VPD attach/update, mode sense/select fallbacks, internal command retry/failure matching, runtime PM stubs, and pseudo-device checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_device.h -->
