# sources/distributed-fs/ceph-client/drivers/block/mtip32xx/mtip32xx.h

## Purpose
This header defines constants, flags, hardware data structures, request state, port state, and per-device state for the Micron RealSSD PCIe block driver implemented by `mtip32xx.c`.

## Important APIs, Types, And Functions
Key constants cover PCI IDs, driver identity, timeout values, command-slot geometry, scatter-gather limits, BAR selection, FTL rebuild markers, secure erase mode, and the `rssd` minor count. The main enum defines port flag bits (`MTIP_PF_*`) and device flag bits (`MTIP_DDF_*`) plus masks for I/O pausing and stopping.

Important types are `struct smart_attr` for SMART attributes, `struct mtip_work` for per-slot-group completion work, `struct host_to_dev_fis` for ATA register FIS layout, `struct mtip_cmd_hdr` for AHCI command headers, `struct mtip_cmd_sg` for PRD entries, `struct mtip_cmd` for per-request blk-mq private state, `struct mtip_port` for one hardware port, and `struct driver_data` for one PCI device. `DEFINE_HANDLER(group)` generates workqueue handlers that dispatch to `mtip_workq_sdbfx()`.

## Control Flow
The header does not execute code, but it shapes control flow by defining the flags tested by submit, timeout, service-thread, and teardown paths. `MTIP_PF_PAUSE_IO` gates normal NCQ submission while internal command, error handling, secure erase, firmware download, or timeout handling is active. `MTIP_DDF_STOP_IO` gates request acceptance when removal, security lock, over-temperature, write-protect, or rebuild failure is present.

## State And Persistence Behavior
All structures are volatile kernel runtime state. `struct mtip_port` owns MMIO pointers, command/FIS DMA regions, identify/log/SMART buffers, queued-command bitmaps, waitqueue, flags, pause timers, unaligned-slot accounting, and per-slot-group locks. `struct driver_data` owns the PCI device, disk, queue/tag set, product information, service thread, debugfs node, workqueue, NUMA binding, and driver flags. The header stores no persistent configuration.

## Dependencies And Integration Points
The header depends on Linux spinlocks, rwsems, ATA definitions, interrupt/workqueue primitives, DMA address types, blk-mq through opaque request private data in the C file, and AHCI-compatible register semantics. It forms the internal contract between hardware register code, blk-mq request handling, debugfs/sysfs code, and PCI lifecycle code.

## Risks
Many structs mirror hardware ABI layouts and use packed/little-endian fields; accidental field changes can break DMA command interpretation. Flag bits are shared across IRQ, service-thread, ioctl, submit, timeout, and teardown contexts, requiring atomic bit operations and careful ordering. The per-tag math assumes slot groups of 32 commands and a maximum of eight groups.

## Test Signals
Compile-time structure layout coverage comes from building the driver. Runtime test signals are indirect: successful DMA command submission, correct IDENTIFY parsing, correct completion by tag, correct pause/stop behavior from flag masks, and absence of data corruption under high queue depth and unaligned I/O constraints.
