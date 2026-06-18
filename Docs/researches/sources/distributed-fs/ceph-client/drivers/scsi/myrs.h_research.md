# sources/distributed-fs/ceph-client/drivers/scsi/myrs.h

## Purpose

`myrs.h` is the private ABI and controller-state header for the Mylex DAC960 V2 SCSI-interface driver implemented by `myrs.c`. It defines firmware opcodes, IOCTL opcodes, status codes, packed controller reply/request structures, 64-byte command mailbox overlays, status mailbox format, per-command and per-controller driver state, callback typedefs, and register definitions for GEM, BA, and LP controller families.

Like `myrb.h`, this header is firmware-facing. Most structures include byte comments and `__packed` annotations because they are copied to or from controller DMA buffers and MMIO mailboxes.

## Important APIs, Types, and Functions

Top-level constants include `MYRS_MAILBOX_TIMEOUT`, reserved command ids `MYRS_DCMD_TAG` and `MYRS_MCMD_TAG`, line buffer size, monitor intervals, `MYRS_SG_LIMIT`, memory mailbox counts, `MYRS_DCDB_SIZE`, and `MYRS_SENSE_SIZE`. `MYRS_MAX_CMD_MBOX` and `MYRS_MAX_STAT_MBOX` size the coherent command and status rings used by the implementation.

`enum myrs_cmd_opcode` defines firmware command classes: memory copy, SCSI 10-byte passthrough, SCSI 255/256-byte passthrough, logical SCSI 10, logical SCSI 256, and IOCTL. `enum myrs_ioctl_opcode` defines controller management operations such as get controller/logical/physical info, get health status, get event, discovery, set device state, initialization control, rebuild control, consistency check, memory mailbox setup, reset, flush, pause, locate, configuration changes, physical-to-logical translation, and clear configuration. `MYRS_STATUS_*` constants are one-byte completion statuses.

Controller/device information structures are `struct myrs_ctlr_info`, `struct myrs_ldev_info`, `struct myrs_pdev_info`, `struct myrs_fwstat`, and `struct myrs_event`. They provide controller model/firmware/hardware/cache/memory/CPU/error/long-operation counts, logical-drive state and progress LBAs, physical-device state and counters, health/event sequence information, and individual event records.

Firmware identity and addressing types include `enum myrs_devstate`, `enum myrs_raid_level`, `enum myrs_stripe_size`, `enum myrs_cacheline_size`, `struct myrs_pdev`, `struct myrs_ldev`, `enum myrs_opdev`, and `struct myrs_devmap`. Transfer types include `struct myrs_cmd_ctrl`, `struct myrs_cmd_tmo`, `struct myrs_sge`, and `union myrs_sgl`.

`union myrs_cmd_mbox` is the central 64-byte firmware command layout. It has views for `common`, `SCSI_10`, `SCSI_255`, `ctlr_info`, `ldev_info`, `pdev_info`, `get_event`, `set_devstate`, `cc`, `set_mbox`, and `dev_op`. `struct myrs_stat_mbox` is the completion record carrying id, firmware status, sense length, and residual.

Driver runtime types are `struct myrs_cmdblk` and `struct myrs_hba`. `myrs_cmdblk` stores a mailbox plus completion status, autosense metadata, residual, completion pointer, optional S/G pool block, optional long CDB buffer, and sense buffer. `myrs_hba` stores MMIO/PCI/SCSI state, model/firmware strings, health/event tracking, monitor flags, workqueue, locks, DMA pools, hardware callbacks, mailbox rings, command blocks, firmware health/controller/event buffers, and mutexes.

The inline helper `dma_addr_writeql()` writes a `dma_addr_t` to two adjacent 32-bit MMIO registers for controllers that accept 64-bit DMA addresses as two dwords.

## Control Flow

The structures in this header support the `myrs.c` probe and I/O flow. During probe, implementation code allocates `struct myrs_hba`, maps controller registers, chooses a `struct myrs_privdata` entry, allocates command/status mailboxes sized by this header, fills a `set_mbox` mailbox with the ring DMA addresses and health buffer DMA address, and submits it through a family-specific hardware mailbox init function.

Direct and monitor commands use `struct myrs_cmdblk` instances embedded in `myrs_hba`. The implementation fills one of the IOCTL mailbox views, points `union myrs_sgl` at a DMA buffer for firmware output, submits it, and waits for a `struct myrs_stat_mbox` completion. Normal SCSI I/O uses per-request `struct myrs_cmdblk` storage from `scsi_cmd_priv()`, fills `SCSI_10` or `SCSI_255`, maps data S/Gs into `union myrs_sgl`, and receives status through the same status ring.

Controller state queries fill `struct myrs_ctlr_info`, which then drives SCSI host limits: physical/virtual channel counts, target counts, queue depth, maximum transfer size, and S/G table size. Logical and physical discovery fill `struct myrs_ldev_info` and `struct myrs_pdev_info` and store those records as per-device hostdata.

Monitoring uses `struct myrs_fwstat` to detect epoch and event sequence changes. `struct myrs_event` records are fetched by event number and decoded by implementation code. Long-running operation fields in `myrs_ctlr_info`, `myrs_ldev_info`, and `myrs_pdev_info` drive progress reporting for rebuild, background initialization, foreground initialization, migration, patrol, and consistency check.

The GEM, BA, and LP register sections provide the constants used by the family-specific init and interrupt handlers. Each family defines inbound doorbell bits, outbound doorbell/status bits, interrupt mask bits, error status bits, and register offsets. `struct myrs_privdata` binds those offsets and helper functions to a PCI id.

## State and Persistence Behavior

This header defines volatile kernel state and firmware DMA layouts. `struct myrs_hba` fields persist for the life of a probed controller: coherent mailbox rings, firmware health buffer, cached controller information, event buffer, monitor scheduling state, and DMA pools. `struct myrs_cmdblk` state persists only for an active command, except the embedded direct and monitor command blocks that are reused serially.

`struct myrs_ctlr_info` is a cached snapshot of controller firmware state. It includes many counters and long-duration activity fields, but those values are authoritative only when freshly read from firmware. `struct myrs_ldev_info` and `struct myrs_pdev_info` snapshots are similarly used as cached per-device state and refreshed by monitor/sysfs paths.

The header exposes firmware operations that can affect persistent controller or array state, including configuration create/delete/clear/add, device state changes, rebuild, initialization, consistency check, device reset, flush, pause, locate, and physical-to-logical translation. The persistence is owned by the controller firmware and disks, not by files in the host filesystem.

The command/status mailbox rings and health buffer are coherent DMA objects whose addresses are stored by firmware after `MYRS_IOCTL_SET_MEM_MBOX`. Their lifetime and alignment are critical: firmware can DMA completions and health data into them asynchronously while the driver is active.

## Dependencies and Integration Points

The header depends on kernel integer types, DMA address types, SCSI host types, PCI types, workqueue types, locks, completions, MMIO accessors, and `irq_handler_t` through its inclusion context. It is tightly integrated with Linux SCSI midlayer request-private command storage and with the RAID class through fields consumed by `myrs.c`.

Firmware integration is the DAC960 V2 SCSI-interface command ABI. `union myrs_cmd_mbox`, `union myrs_sgl`, `struct myrs_stat_mbox`, and the controller/device/event structures are shared with the controller via DMA or hardware mailbox submission.

Hardware integration is defined by the GEM, BA, and LP register constants. The implementation writes doorbells, command mailbox addresses, interrupt masks, status acknowledgments, and reset bits using these offsets. `dma_addr_writeql()` bridges Linux `dma_addr_t` values to the controller's two-register 64-bit address programming model.

## Risks and Edge Cases

The many packed bitfield structures are ABI-sensitive. Bitfield order, enum size, packing, and endianness must remain compatible with the controller firmware. Any compiler or architecture change that alters these assumptions can corrupt mailbox or reply interpretation.

`union myrs_cmd_mbox` overlays fields with different declared widths, including 24-bit bitfields for DMA size in IOCTL views and full 32-bit `dma_size` in SCSI views. Implementation code must fill the union view matching the opcode; reading a field through another view is fragile even when the current layout overlaps.

`MYRS_SENSE_SIZE` is 14 bytes, smaller than the generic SCSI sense buffer. The driver copies only firmware-reported sense length up to `SCSI_SENSE_BUFFERSIZE`, but the allocated firmware autosense area is fixed by this header. Commands needing larger autosense data may lose detail.

The firmware mailbox counts and S/G limits are fixed constants. The implementation caps host limits against these values, but any new hardware reporting higher queue depth or S/G capacity cannot use it without changing the ABI handling and pool sizing.

`struct myrs_pdev_info` reserves a large trailing area, and `myrs.c` reuses part of `rsvd13` as a `struct myrs_devmap` scratch area in one path. That is space-efficient but fragile because it treats reserved firmware output bytes as host-owned temporary storage.

Register definitions differ subtly between GEM, BA, and LP. For example, "mailbox full" and "initialization in progress" bits have inverted meanings in some families. Family-specific helper code must use the matching constants exactly.

## Test Signals

Compile-time validation should include `sizeof()` and `offsetof()` checks for firmware-visible structures if this header is edited, especially `struct myrs_ctlr_info`, `struct myrs_ldev_info`, `struct myrs_pdev_info`, `union myrs_cmd_mbox`, and `struct myrs_stat_mbox`. Sparse or static-analysis runs should inspect packed bitfields and union aliasing.

Runtime validation should confirm that `SET_MEM_MBOX` programs command/status rings correctly, status mailbox completion ids map to direct, monitor, and SCSI request command blocks, and health/event buffers update through DMA. Discovery tests should verify controller info sizing, physical and logical device info parsing, RAID level mapping, and physical-to-logical translation.

Hardware-family tests should exercise GEM, BA, and LP register paths for init polling, error-status reads, mailbox submission, interrupt masking/unmasking, status acknowledgment, and reset. Fault-injection tests should cover DMA allocation failures, mailbox timeout, invalid status ids, and firmware-reported limits exceeding `MYRS_MAX_CMD_MBOX`, `MYRS_MAX_STAT_MBOX`, or `MYRS_SG_LIMIT`.
