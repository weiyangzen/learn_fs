# sources/distributed-fs/ceph-client/drivers/scsi/myrb.h

## Purpose

`myrb.h` is the private hardware and firmware ABI header for the block-command-era Mylex DAC960/AcceleRAID/eXtremeRAID PCI RAID controller driver. It describes the older DAC960 V1 firmware interface: command opcodes, status codes, packed controller reply buffers, physical and logical device records, mailbox layouts, DMA helper records, controller-private host state, and register definitions for LA, PG, and PD controller families.

The file is not an implementation unit; it is the contract consumed by the matching V1 driver code. Most definitions are byte-annotated and `__packed`, so this header is part of the firmware-visible ABI rather than ordinary in-kernel data modeling.

## Important APIs, Types, and Functions

Key constants size the driver's view of the hardware: `MYRB_MAX_LDEVS`, `MYRB_MAX_CHANNELS`, `MYRB_MAX_TARGETS`, `MYRB_SCATTER_GATHER_LIMIT`, `MYRB_CMD_MBOX_COUNT`, `MYRB_STAT_MBOX_COUNT`, `MYRB_MAILBOX_TIMEOUT`, `MYRB_DCMD_TAG`, and `MYRB_MCMD_TAG`. Monitor intervals are split into primary and secondary polling periods.

`enum myrb_cmd_opcode` enumerates V1 firmware commands for extended and legacy reads/writes, DCDB passthrough, flush, enquiry, logical/physical device state, event log reads, rebuild, consistency check, background initialization, configuration, firmware image, diagnostic, and subsystem operations. The many `MYRB_STATUS_*` constants define command completion meanings, but several status values are reused across command families, so callers must interpret them in opcode context.

Firmware reply and request structures include `struct myrb_enquiry`, `struct myrb_enquiry2`, `struct myrb_ldev_info`, `struct myrb_pdev_state`, `struct myrb_log_entry`, `struct myrb_rbld_progress`, `struct myrb_bgi_status`, `struct myrb_error_entry`, `struct myrb_config2`, and `struct myrb_dcdb`. These model controller state, logical drive state, physical drive state, event log payloads, rebuild/background initialization progress, error counters, configuration flags, and direct SCSI command descriptor blocks.

`union myrb_cmd_mbox` is the core V1 submission ABI. It overlays the 16-byte command mailbox with opcode-specific views such as `common`, `type3`, `type3B`, `type3C`, `type3D`, `type3E`, `type3R`, `type4`, `type5`, and `typeX`. `struct myrb_stat_mbox` is the corresponding status mailbox record with command id, valid bit, and 16-bit status.

Driver-owned runtime types are `struct myrb_cmdblk`, which wraps a mailbox, completion status, optional DCDB, and optional S/G list, and `struct myrb_hba`, which stores controller geometry, feature flags, PCI/SCSI objects, workqueue and monitor state, DMA pools, mailbox rings, direct/monitor command blocks, enquiry/error/logical-device buffers, and hardware callback pointers. `struct myrb_privdata` selects a controller-family hardware initializer, IRQ handler, and MMIO size.

The bottom half of the header defines register offsets and bit masks for LA, PG, and PD controller interfaces, plus callback typedefs `myrb_hw_init_t` and `mbox_mmio_init_t`. These register constants are consumed by low-level code that polls doorbells, acknowledges status, masks interrupts, and resets controllers.

## Control Flow

The intended runtime flow is mailbox based. The driver allocates command and status mailbox rings, fills a `union myrb_cmd_mbox` variant for the operation it wants, uses controller-family register callbacks to notify the adapter, and later consumes a `struct myrb_stat_mbox` completion. Direct commands use reserved tag `MYRB_DCMD_TAG`; monitor commands use `MYRB_MCMD_TAG`; normal SCSI commands use other ids.

Controller discovery starts with enquiry commands. `MYRB_CMD_ENQUIRY` fills `struct myrb_enquiry` with drive counts, logical drive sizes, rebuild/check state, event sequence, battery presence, and dead drive locations. `MYRB_CMD_ENQUIRY2` fills `struct myrb_enquiry2` with controller model, firmware version, channel limits, memory/cache sizes, command limits, block sizes, SCSI bus capabilities, and firmware feature bits. Logical and physical discovery then use `MYRB_CMD_GET_LDEV_INFO` and `MYRB_CMD_GET_DEVICE_STATE`.

Read/write I/O uses `type4` or `type5` mailbox views depending on whether the command is direct or scatter/gather. `type5` carries the compact logical-drive transfer fields, LBA, DMA address, S/G count, and S/G type. DCDB commands use `struct myrb_dcdb` to tunnel SCSI CDBs to physical devices with DMA direction, timeout, autosense, CDB length, sense buffer, and device status.

Monitoring and management flows are represented by event, rebuild, consistency, background initialization, and error-table structures. The driver tracks `new_ev_seq` and `old_ev_seq` in `struct myrb_hba`, reads event log entries, reports rebuild/background initialization progress, and keeps flags such as `need_ldev_info`, `need_err_info`, `need_rbld`, `need_cc_status`, and `need_bgi_status` to decide which firmware queries should run in the monitor work item.

## State and Persistence Behavior

This header defines in-memory kernel state and controller firmware state, not file-backed persistence. Persistent side effects happen on the RAID controller through firmware commands: configuration writes, rebuild/control operations, background initialization, bad-data table operations, capacity expansion, firmware image updates, and device state changes.

`struct myrb_hba` owns long-lived kernel state for one adapter. It caches geometry (`ldev_block_size`, heads/sectors, stripe/segment size), feature flags (`dual_mode_interface`, `bgi_status_supported`, `safte_enabled`), mailbox ring positions, DMA allocations, command blocks, enquiry data, error tables, logical device information, and progress state. The monitor work fields and event sequence fields make controller state updates incremental across polling periods.

The packed firmware structures persist only as snapshots. For example, `struct myrb_enquiry` and `struct myrb_enquiry2` report current controller state; `struct myrb_config2` mirrors firmware configuration bytes and checksum; `struct myrb_error_entry` records counters; `struct myrb_log_entry` carries a single event. Callers must refresh these buffers from firmware when they need current state.

## Dependencies and Integration Points

`myrb.h` depends on Linux kernel types and subsystems made available by its including C file: PCI, SCSI host integration, DMA pools, completions, workqueues, delayed work, mutexes, spinlocks, MMIO accessors, and `irq_handler_t`. It integrates with the Mylex DAC960 V1 firmware via byte-exact packed command and reply structures.

Hardware integration is split by controller family. LA, PG, and PD register definitions describe doorbells, command mailbox byte registers, status registers, interrupt masks, and error status registers. The `myrb_privdata` table in implementation code can bind a PCI id to the proper register layout and initialization sequence.

SCSI integration is indirect through command blocks and logical/physical device structures. Logical drives are exposed using `struct myrb_ldev_info` and controller geometry, while physical devices and SCSI passthrough use `struct myrb_pdev_state` and `struct myrb_dcdb`.

## Risks and Edge Cases

The file relies heavily on C bitfields in `__packed` hardware ABI structures. Bitfield layout is compiler and endian sensitive, so this code assumes the kernel/compiler conventions used by the target architecture match the firmware layout. The byte comments are useful for review but are not compile-time guarantees.

Status values are reused for different command families. A generic status decoder can easily mislabel failures unless it considers the opcode or operation class. `MYRB_STATUS_CHECK_CONDITION` also overlaps with logical-drive offline status in some contexts.

Several firmware buffers contain fixed-size arrays tied to old controller limits, such as 32 logical devices, 45 physical devices, 21 dead drives, 6 channel parameters, and 32 S/G entries. Any caller must clamp firmware-reported values to these constants before indexing.

Mailbox and DMA address fields are mostly 32-bit (`u32`) in the V1 ABI. Systems with high DMA addresses require implementation-side DMA mask handling or bounce behavior that keeps firmware-visible addresses representable.

Progress reporting structures use controller block counts and fields such as `blocks_left`, `blocks_done`, and logical device size. Callers must avoid division by zero and must handle in-progress status codes that can mean valid data, failure, success, or termination depending on the query.

## Test Signals

Build coverage should catch syntax and type drift, but ABI drift needs stronger checks: inspect `sizeof()` and `offsetof()` for firmware-visible structures if this header changes. Probe tests should include LA, PG, and PD family devices or emulation paths, command/status mailbox wraparound, interrupt acknowledge paths, and reset/init timeout handling.

Functional validation should exercise enquiry/enquiry2 discovery, logical-device info refresh, physical-device state reads, event-log sequence handling, DCDB passthrough with and without autosense, S/G read/write I/O at the 32-entry limit, cache flush, rebuild and consistency-check monitoring, and error-table updates. Fault injection should cover DMA allocation failures, invalid firmware status values, mailbox timeout, and firmware-reported counts larger than the driver constants.
