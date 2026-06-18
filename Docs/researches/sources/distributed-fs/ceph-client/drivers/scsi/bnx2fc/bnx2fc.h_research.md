# sources/distributed-fs/ceph-client/drivers/scsi/bnx2fc/bnx2fc.h

## Purpose

`bnx2fc.h` is the central private header for the QLogic/Broadcom FCoE offload driver. It gathers Linux, SCSI, libfc, libfcoe, FC, firmware-HSI, CNIC, and bnx2x headers; defines driver limits; declares global state; defines HBA, interface, rport, command, command-manager, middle-path, and work structures; and exposes cross-file prototypes.

## Important APIs, Types, and Definitions

Identity and limits include `BNX2FC_NAME`, `BNX2FC_VERSION`, queue sizes, max BDs, max sessions, NPIV limits, payload/MFS sizes, XID ranges, LUN/target limits, command length, TM timeout, firmware timeout, and retry counts. `struct bnx2fc_hba` stores per-adapter CNIC/PCI/netdev state, command manager, locks, flags, XID/task limits, firmware DMA memory, stats, waits, and vports. `struct bnx2fc_interface` binds an FCoE controller to a netdev/HBA. `struct bnx2fc_rport` stores per-offloaded-session queues, DMA addresses, context IDs, flags, locks, timers, and wait queues. `struct bnx2fc_cmd` represents SCSI, TMF, ABTS, ELS, cleanup, and sequence-cleanup commands.

## Control Flow

The header defines the layering: `bnx2fc_fcoe.c` manages module/libfc/libfcoe/CNIC lifecycle, `bnx2fc_hwi.c` manages firmware queues and task contexts, `bnx2fc_io.c` and `bnx2fc_tgt.c` handle SCSI and rport flows, and `bnx2fc_els.c` handles ELS/recovery. Runtime commands allocate `bnx2fc_cmd`, initialize firmware task context, post SQEs, and complete through CQ/KCQ paths back to SCSI/libfc.

## State and Persistence Behavior

State is in-memory and DMA-visible, not disk-persistent. HBA state persists for CNIC device lifetime, interface state for FCoE controller lifetime, rport state for offloaded session lifetime, and command state for XID lifetime. Bit flags in HBA, interface, rport, and command objects coordinate timers, completions, link events, and teardown.

## Dependencies and Integration Points

The header integrates with SCSI mid-layer, FC transport, libfc, libfcoe, netdevice packet handlers, PCI/DMA APIs, kernel threads/workqueues/timers, CNIC ULP callbacks, and bnx2x firmware capability headers.

## Risks and Edge Cases

The broad shared state makes locking and lifetime rules critical. Queue constants must match firmware limits. Several flags are bit indexes, not masks. Command lifetime spans SCSI, ELS, ABTS, and cleanup paths, so callback and timer code must avoid double release.

## Test Signals

Test module load/unload, controller create/destroy, link events, NPIV, session offload/upload, SCSI queueing with max SG/queue depth, TMF/ABTS/cleanup paths, ELS recovery, CPU hotplug, debug logging, and DMA/race checking under teardown.
