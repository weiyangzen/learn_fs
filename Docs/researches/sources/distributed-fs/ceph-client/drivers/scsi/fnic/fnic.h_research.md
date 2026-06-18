# sources/distributed-fs/ceph-client/drivers/scsi/fnic/fnic.h

## Purpose

`fnic.h` is the central private header for the Cisco FNIC FCoE HBA driver. It defines driver identity, PCI IDs, SCSI command-private state, I/O and reset flags, logging macros, queue sizing, interrupt indexes, driver state enums, event structures, the main `struct fnic`, cross-file prototypes, SCSI iteration helpers, and debug dump helpers.

## Important APIs, Types, and Definitions

- Driver metadata: `DRV_NAME`, `DRV_DESCRIPTION`, `DRV_VERSION`, and logging prefixes.
- I/O tags and flags: special abort/device-reset tag bits, `FNIC_TAG_MASK`, and many `FNIC_IO_*`/`FNIC_DEV_RST_*` bits used by SCSI command state machines.
- `struct fnic_cmd_priv`, `fnic_priv()`, and `fnic_flags_and_state()`: per-SCSI-command private data and compact state/flag reporting.
- Reset and RSCN enums: reset progress, RSCN type, PCRSCN handling state, and feature flag.
- Logging macros: `FNIC_MAIN_DBG`, `FNIC_FCS_DBG`, `FNIC_FIP_DBG`, `FNIC_SCSI_DBG`, and `FNIC_ISR_DBG`, gated by `fnic_log_level`.
- Interrupt and driver state enums: INTx/MSI-X indexes and `enum fnic_state` for FC/Ethernet transition modes.
- `struct fnic_frame_list`, `struct fnic_event`, and `struct fnic_cpy_wq`: queued frame/event and copy-work-queue software state.
- `struct fnic`: per-adapter state for SCSI host, vNIC resources, interrupt resources, reset state, stats, link/FIP/FDLS state, workqueues, frame queues, target events, mempools, work/copy/receive/completion queues, and locks.
- Cross-file prototypes for interrupt setup, frame/link/event handlers, queue completion handlers, SCSI host callbacks, reset paths, debugfs/stats, FIP/FDLS operations, target handling, queue counting, unload cleanup, and debug info.
- `fnic_scsi_io_iter()`: wrapper around `scsi_host_busy_iter()` for applying a callback to outstanding SCSI commands.

## Control Flow and Design Role

This header defines the driver layering. `fnic_main.c` allocates and initializes `struct fnic`, vNIC queues, interrupts, mempools, timers, and the `iport`. ISR and CQ handlers use queue arrays and interrupt indexes from this header. `fnic_scsi.c` uses the command-private fields, tag flags, state flags, and SCSI prototypes. `fdls_disc.c` and `fip.c` use the embedded `iport`, frame queues, work items, timers, VLAN state, and logging macros. Sysfs/debugfs files expose fields declared here.

## State and Persistence Behavior

`struct fnic` is the primary per-device in-memory state object. It persists from PCI probe through remove and includes hardware resources, queue state, work items, timers, locks, FIP/FDLS state, SCSI host pointer, mempools, stats, and reset/removal flags. Command-private state persists for each outstanding SCSI command. `state_flags` is protected by the SCSI host lock, while many FDLS/FIP fields are protected by `fnic_lock`, `vlans_lock`, target-list locks, or queue-specific locks. No disk persistence is performed.

## Dependencies and Integration Points

`fnic.h` depends on Linux interrupt, netdevice, workqueue, bitops, SCSI command/transport, FC frame, vNIC resource/queue/interrupt/stats headers, FNIC I/O/stats/trace headers, and `fnic_fdls.h`. It is included by nearly every FNIC source file and is the main integration point between PCI/vNIC hardware, Linux SCSI transport, FDLS/FIP discovery, debugfs, sysfs, and reset handling.

## Risks and Edge Cases

- `struct fnic` is broad shared mutable state; wrong lock usage can affect SCSI I/O, discovery, reset, and remove paths.
- Command flags and states are bitmasks shared across abort/reset/completion paths; double completion or stale `io_req` pointers are major risks.
- Queue-count constants define array sizes for MSI-X, CQs, work queues, and receive queues. Mismatched hardware negotiation can overrun or underutilize queues.
- State transitions between FC mode and Ethernet/FIP mode must coordinate link events, FIP timers, firmware reset, and blocked I/O flags.
- Logging macros are compile-time safe but runtime-heavy if enabled at high volume in IRQ or completion paths.

## Test Signals

Useful signals include successful probe/remove, interrupt-mode selection, queue allocation and completion handling, SCSI command private state transitions, abort/device-reset/host-reset handling, firmware reset blocking/unblocking I/O, link up/down mode transitions, FIP/FDLS startup, debugfs/sysfs exposure, multi-queue mapping, outstanding I/O counting, and unload cleanup with active target ports.
