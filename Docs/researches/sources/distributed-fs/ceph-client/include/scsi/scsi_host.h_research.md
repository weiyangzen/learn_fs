<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_host.h -->
# sources/distributed-fs/ceph-client/include/scsi/scsi_host.h

## Purpose
This header defines the SCSI host adapter template and `struct Scsi_Host`, the mid-layer representation of an HBA or virtual SCSI host. It is the main contract between LLDDs, transports, block multiqueue, scanning, error handling, protection information, and sysfs/proc integration.

## Important APIs, Types, And Functions
`struct scsi_host_template` declares queueing, reserved queueing, commit, info, ioctl/compat ioctl, command-private init/exit, EH handlers, device/target allocation/configuration/destruction, scan callbacks, queue-depth changes, queue mapping/polling, DMA drain, BIOS params, native capacity unlock, timeout/retry hooks, host reset, capacity/SG/DMA limits, mode flags, attribute groups, and vendor ID. `enum scsi_timeout_action`, `enum scsi_host_state`, `struct Scsi_Host`, `DEF_SCSI_QCMD`, protection capability enums, guard enums, and helpers like `shost_priv()`, `dev_to_shost()`, `scsi_host_in_recovery()`, `scsi_add_host()`, scan/remove/get/put/block/unblock APIs are central.

## Control Flow
Drivers fill a host template, allocate a host, add it with a parent/DMA device, scan it, accept commands through `queuecommand`, and complete them asynchronously. EH callbacks run in the EH thread with normal queueing stopped. Host state controls scanning, recovery, deletion, and request blocking. Transport templates may add host/target/device private data and workqueues.

## State And Persistence
`Scsi_Host` stores device/target lists, locks, scan mutex, EH queues/thread, blk-mq tag set, host failure counters, IDs/limits, queue capabilities, runtime mode bits, workqueues, PI capabilities, legacy I/O fields, sysfs devices, pseudo-device, transport data, DMA device, autosuspend delay, and aligned driver private hostdata. State is volatile but exposed through sysfs/proc.

## Dependencies And Integration Points
It depends on block, device, workqueue, SCSI device/command/transport concepts, and optional procfs. It is used by all SCSI LLDDs and transport classes including SAS, FC, iSCSI, SPI, and SRP.

## Risks
`queuecommand` return semantics are strict: accepted commands must complete, rejected commands must not be touched. EH context must not race normal queueing. Host/device private data sizing must align with transport reservations. Host-wide tagsets and queue mapping affect block-layer concurrency. State changes require the mid-layer enforcer.

## Test Signals
Validate host allocation/add/remove/lookup, queuecommand accept/reject/commit paths, reserved commands, EH handlers and timeouts, scan callbacks, queue limits, host block/unblock, busy iteration, PI/DIX capability helpers, guard type settings, procfs conditional builds, and driver-private data offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/scsi_host.h -->
