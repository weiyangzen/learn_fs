# Research: subset-b-005223

This grouped report covers the requested SCSI driver files under `sources/distributed-fs/ceph-client/drivers/scsi`. Each source file section is delimited for deterministic splitting into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/NCR5380.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/NCR5380.c

## Purpose

`NCR5380.c` is the generic Linux SCSI low-level core for NCR 5380/53C80-style SCSI protocol controllers and related 53C400-family variants. It is designed to be included by board-specific wrapper drivers that provide register access and optional DMA or pseudo-DMA hooks through macros declared before including this file. The file implements the SCSI initiator state machine: command queueing, arbitration, target selection, message/CDB/status/data phases, disconnection and reselection, autosense, interrupt handling, DMA completion, abort, and host reset.

## Important APIs, Types, and Functions

- `NCR5380_init(struct Scsi_Host *instance, int flags)` initializes `struct NCR5380_hostdata`, SCSI host limits, workqueue, queues, chip registers, masks, and register polling calibration.
- `NCR5380_queue_command(struct Scsi_Host *instance, struct scsi_cmnd *cmd)` is the SCSI mid-layer queue entry point. It enqueues commands on `unissued`, prioritizes `REQUEST_SENSE`, acquires any board DMA IRQ resource, and schedules `main_task`.
- `NCR5380_main(struct work_struct *work)` is the coroutine-like main loop. It selects new commands when no nexus is active, runs information transfer when connected, re-enables reselection interrupts when idle, and releases DMA IRQ resources when all queues drain.
- `NCR5380_select()` arbitrates for the SCSI bus, selects a target, sends the `IDENTIFY` message, initializes the command transfer pointer, sets `connected`, and marks the target/lun busy.
- `NCR5380_information_transfer()` is the phase dispatcher for DATA IN/OUT, COMMAND OUT, STATUS IN, MESSAGE IN/OUT. It performs PIO/DMA transfers, handles disconnects, command completion, autosense queueing, message rejection, and reset-on-lost-BSY handling.
- `NCR5380_intr()` handles chip interrupts for DMA end/phase mismatch/loss of BSY, reselection, and bus reset conditions.
- `NCR5380_transfer_pio()` implements REQ/ACK handshaking for byte-wise transfers.
- `NCR5380_transfer_dma()` sets up real or pseudo-DMA, handles 5380 DMA errata workarounds, and delegates completion to `NCR5380_dma_complete()`.
- `NCR5380_reselect()` accepts target reselection and matches it against the disconnected command list.
- `NCR5380_abort()` and `NCR5380_host_reset()` implement SCSI EH hooks.
- Internal helpers include `initialize_SCp()`, `advance_sg_buffer()`, `set_resid_from_SCp()`, `complete_cmd()`, `dequeue_next_cmd()`, `requeue_cmd()`, `do_abort()`, `do_reset()`, and `bus_reset_cleanup()`.

## Control Flow

The normal command path starts at `NCR5380_queue_command()`, which links the private `NCR5380_cmd` into `hostdata->unissued` or puts sense commands at the front. `NCR5380_main()` repeatedly dequeues commands that do not conflict with the per-target/lun busy bitmap. It calls `NCR5380_select()` to win arbitration, assert selection, send `IDENTIFY`, set `connected`, and initialize the scatterlist pointer state. Once connected, `NCR5380_main()` calls `NCR5380_information_transfer()`.

`NCR5380_information_transfer()` runs one or more SCSI bus phases. For data phases it advances through scatterlist entries and prefers `NCR5380_transfer_dma()` when the board hook reports a positive transfer size and the device is not marked `borken`; otherwise it performs bounded PIO chunks to avoid holding the IRQ-mode lock for long periods. COMMAND OUT sends the CDB, STATUS IN records target status, MESSAGE IN handles `COMMAND_COMPLETE`, `DISCONNECT`, pointer messages, extended negotiation messages, and rejects unknown messages by asserting ATN and preparing `MESSAGE_REJECT`. A complete command clears `connected`, clears the busy bit, sets residuals and result status, and either calls `complete_cmd()` or queues autosense for check-condition-like statuses.

If a target sends `DISCONNECT`, the command moves to `disconnected` and later returns through `NCR5380_intr()` when the target reselects. The interrupt handler disables selection interrupts, calls `NCR5380_reselect()`, and requeues the main worker. `NCR5380_reselect()` validates the target mask, handshakes the identify message, finds the matching command by target and LUN, removes it from `disconnected`, and restores it as `connected`.

Error recovery traces the same state graph. `NCR5380_abort()` searches `unissued`, `selecting`, `disconnected`, `connected`, and `autosense`, completing or forgetting the command as required by SCSI EH ownership. `NCR5380_host_reset()` completes queued work with `DID_RESET`, pulses reset through `do_reset()`, and lets `bus_reset_cleanup()` reset registers, queues, busy bits, and DMA state.

## State and Persistence Behavior

Runtime state lives in `struct NCR5380_hostdata`, primarily protected by `hostdata->lock`. Persistent kernel-visible state includes SCSI host registration and the per-host workqueue; there is no disk persistence. Important mutable fields are `connected`, `selecting`, `unissued`, `autosense`, `disconnected`, `sensing`, `ses`, `busy[8]`, `dma_len`, `read_overruns`, `last_message`, `poll_loops`, and the board quirk flags. Per-command state lives in `struct NCR5380_cmd`, stored as SCSI command private data and tracking current SG entry, pointer, residual, target status, and current phase.

The driver deliberately performs an implicit SAVE POINTERS operation on disconnect, preserving the current command data pointer even when broken disks omit the SCSI-standard `SAVE_POINTERS` message. Autosense state is staged through `hostdata->sensing` and `hostdata->ses`, allowing `scsi_eh_prep_cmnd()` and `scsi_eh_restore_cmnd()` to temporarily turn the original command into a request-sense command.

## Dependencies and Integration Points

This file depends on `NCR5380.h` definitions and on board wrapper macros/functions: `NCR5380_read`, `NCR5380_write`, `NCR5380_implementation_fields`, `NCR5380_dma_xfer_len`, `NCR5380_dma_send_setup`, `NCR5380_dma_recv_setup`, and `NCR5380_dma_residual`; optional wrappers include I/O delay and DMA IRQ acquire/release hooks. It integrates with the SCSI mid-layer via `scsi_done()`, residual/result helpers, SCSI EH APIs, scatterlist access, request sense preparation, SPI message printing, and host workqueues. Conditional Sun3 paths integrate with Sun3 DMA globals and VME CSR handling.

## Risks

- The driver intentionally releases `hostdata->lock` during slow arbitration, selection, and some message paths, so correctness relies on careful `selecting` and `connected` checks after reacquiring the lock.
- Register polling and PIO handshaking can spin with interrupts disabled in some call paths; wedged or non-compliant devices can stress latency.
- DMA errata handling is subtle. `FLAG_DMA_FIXUP`, `read_overruns`, and late DMA setup behavior all depend on board-specific hooks reporting accurate transfer sizes and residuals.
- `busy[8]` assumes narrow target indexing in the generic core and uses LUN bitmasks; unusual LUN ranges or target assumptions in wrappers need care.
- The `disconnect_mask` module parameter changes whether devices may disconnect. Bad settings can reduce concurrency or expose old device quirks.
- Bus reset cleanup completes and empties multiple queues under the lock; any wrapper invoking reset paths must not leave board DMA hardware active.

## Test Signals

Useful validation signals include successful host initialization with correct `hostdata->info`, queue/dequeue operation under concurrent I/O, data transfers across SG boundaries, check-condition autosense, disconnect/reselect cycles, DMA and PIO fallback behavior, aborting commands in each state (`unissued`, `selecting`, `disconnected`, `connected`, `autosense`), and host reset after lost BSY or bus reset interrupt. Debug builds can use `NDEBUG_*` masks to trace phases, queues, arbitration, DMA, reselection, and abort paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/NCR5380.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/NCR5380.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/NCR5380.h

## Purpose

`NCR5380.h` defines the register map, bit masks, phase constants, debug masks, private state structures, inline helpers, and generic function prototypes used by the NCR 5380 SCSI core and board-specific wrapper drivers. It is the contract between `NCR5380.c` and platforms that provide chip register access plus optional DMA support.

## Important APIs, Types, and Functions

- Register constants cover the 5380 data, initiator command, mode, target command, status, select-enable, bus/status, DMA-start, input-data, and interrupt-reset registers.
- Bit definitions describe SCSI signal state (`SR_*`), bus/status flags (`BASR_*`), initiator command outputs (`ICR_*`), mode bits (`MR_*`), and 53C400 CSR bits (`CSR_*`).
- Phase constants (`PHASE_DATAOUT`, `PHASE_DATAIN`, `PHASE_CMDOUT`, `PHASE_STATIN`, `PHASE_MSGOUT`, `PHASE_MSGIN`, `PHASE_UNKNOWN`) encode SCSI bus phase interpretation from status register bits.
- `struct NCR5380_hostdata` holds board fields supplied by `NCR5380_implementation_fields`, I/O pointers, queues, lock, workqueue, command nexus state, DMA state, host identity masks, busy bitmap, autosense state, quirk flags, and info text.
- `struct NCR5380_cmd` is per-SCSI-command private data: current memory pointer, residual in current SG entry, current SG entry, status, phase, and list node.
- `NCR5380_to_scmd()` and `NCR5380_to_ncmd()` translate between `struct scsi_cmnd` and the private command state.
- Prototypes expose the generic implementation functions to include-style wrapper drivers.
- `NCR5380_poll_politely()` wraps `NCR5380_poll_politely2()` for single-register waits.
- `NCR5380_dma_xfer_none()`, `NCR5380_dma_setup_none()`, and `NCR5380_dma_residual_none()` are no-DMA fallback hooks.

## Control Flow

This header does not execute control flow by itself, but it defines the values that drive all phase transitions in `NCR5380.c`. The core reads `STATUS_REG`, masks it with `PHASE_MASK`, converts it to target-command register bits with `PHASE_SR_TO_TCR()`, and uses the register masks here to drive arbitration, selection, transfer, interrupt acknowledgment, and reset sequencing. The function prototypes assume a wrapper includes this header and the generic `.c` after defining the required access macros.

## State and Persistence Behavior

The header defines in-memory, per-host and per-command state only. `struct NCR5380_hostdata` persists for the lifetime of the `Scsi_Host`; queue heads and workqueue state survive across individual commands until driver removal. `struct NCR5380_cmd` persists with each command allocation and is reused by the SCSI mid-layer. No on-disk persistence exists.

## Dependencies and Integration Points

The header includes kernel delay, interrupt, list, workqueue, SCSI debug, SCSI EH, and SPI transport headers. It assumes inclusion from a Linux SCSI low-level driver and depends on wrapper-provided `NCR5380_implementation_fields` and register/DMA functions. Its prototypes reference `struct Scsi_Host`, `struct scsi_cmnd`, and Linux scatterlist state.

## Risks

- The include-style architecture means compile-time macro order matters; missing or incompatible wrapper macros can produce subtle build or runtime failures.
- `struct NCR5380_hostdata` includes board-specific fields through a macro, so ABI/layout assumptions are local to each including driver.
- Some register offsets are read/write aliases; misuse by wrappers or debugging code can cause real bus side effects.
- The per-target `busy[8]` bitmap and LUN bit operations reflect older SCSI assumptions.
- Debug macros are compile-time gated through `NDEBUG`; enabling broad masks may expose timing-sensitive behavior in a low-level bus driver.

## Test Signals

Build coverage should include at least one wrapper with no DMA hooks and one with real or pseudo-DMA hooks. Runtime signals include correct phase decoding, register polling timeouts, debug phase printing, command-private state conversions, and correct hostdata initialization in wrappers that allocate `cmd_size >= sizeof(struct NCR5380_cmd)`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/NCR5380.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a100u2w.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/a100u2w.c

## Purpose

`a100u2w.c` is the PCI SCSI low-level driver for Initio INI-A100U2W / Orchid-based adapters. It initializes the controller firmware and NVRAM, allocates coherent SCSI Control Block arrays, translates Linux SCSI commands into controller SCBs and scatter-gather descriptors, posts SCBs to the hardware FIFO, handles reply interrupts, and implements abort, bus reset, and device reset callbacks.

## Important APIs, Types, and Functions

- Hardware wait helpers: `wait_chip_ready()`, `wait_firmware_ready()`, `wait_scsi_reset_done()`, `wait_HDO_off()`, and `wait_hdi_set()` poll controller mailbox bits.
- NVRAM and firmware helpers: `orc_read_fwrev()`, `orc_nv_read()`, `orc_nv_write()`, `se2_rd_all()`, `se2_update_all()`, `read_eeprom()`, and `orc_load_firmware()`.
- SCB setup and allocation: `setup_SCBs()`, `init_alloc_map()`, `__orc_alloc_scb()`, `orc_alloc_scb()`, and `orc_release_scb()`.
- Submission and reset paths: `orc_exec_scb()`, `orc_reset_scsi_bus()`, `orc_device_reset()`, `orchid_abort_scb()`, and `inia100_abort_cmd()`.
- I/O path: `inia100_build_scb()`, `inia100_queue_lck()`, `inia100_queue`, `orc_interrupt()`, and `inia100_scb_handler()`.
- PCI lifecycle: `inia100_probe_one()`, `inia100_remove_one()`, `inia100_pci_tbl`, `inia100_pci_driver`, and `module_pci_driver()`.
- `inia100_template` supplies SCSI mid-layer callbacks and host limits.

## Control Flow

Probe starts with `pci_enable_device()`, a 32-bit DMA mask, bus mastering, I/O port reservation, `scsi_host_alloc()`, and coherent allocation of `ORC_MAXQUEUE` SCBs plus extended SCBs. `init_orchid()` disables interrupts, resets or reuses firmware depending on readiness and firmware revision, loads 4 KiB firmware from BIOS EEPROM into controller SRAM if needed, initializes SCB base registers, reads NVRAM or restores defaults, copies adapter and target configuration into `struct orc_host`, and enables the reply FIFO interrupt. The driver then fills SCSI host fields, requests a shared IRQ, registers the host, and scans the bus.

The command path starts in `inia100_queue_lck()`. It allocates an SCB from `allocation_map`, calls `inia100_build_scb()` to bind the SCB to the Linux command, maps the command with `scsi_dma_map()`, builds up to `TOTAL_SG_ENTRY` SG descriptors in the extended SCB, sets transfer length, CDB, identify byte, and tag message, then posts the SCB index to `ORC_PQUEUE` through `orc_exec_scb()`. Firmware later places completed SCB indexes in `ORC_RQUEUE`. `inia100_intr()` locks the host and delegates to `orc_interrupt()`, which drains reply queue entries and calls `inia100_scb_handler()` for each SCB.

`inia100_scb_handler()` maps adapter host status to SCSI host bytes, copies fixed-size sense data from the extended SCB area on check condition, composes `cmd->result`, unmaps DMA, calls `scsi_done()`, and releases the SCB back to `allocation_map`. Abort and device reset paths scan active SCBs to find the command, then issue firmware mailbox commands (`ORC_CMD_ABORT_SCB` or an `ORC_BUSDEVRST` SCB). Bus reset reinitializes the allocation map and asserts `SCSIRST`.

## State and Persistence Behavior

Driver state is stored in `struct orc_host` in `shost->hostdata`: I/O base, controller index, SCSI ID, BIOS config, flags, maximum targets, target flags, max tags, coherent SCB/ESCB virtual and DMA addresses, allocation bitmap, PCI device pointer, and allocation spinlock. The global `struct orc_nvram nvram` is a temporary in-kernel copy of EEPROM configuration. The default NVRAM table is used to rewrite invalid EEPROM contents.

The controller owns persistent firmware/NVRAM outside system RAM. This driver can rewrite NVRAM bytes in `se2_update_all()` when checksum or reading fails, and can download firmware from the adapter BIOS image to controller SRAM during initialization. Command state is held in coherent SCB arrays and in `escb->srb` back-pointers until completion.

## Dependencies and Integration Points

The driver depends on PCI, I/O port accessors (`inb/outb/inw/outw/inl/outl`), DMA mapping/coherent allocation, the Linux SCSI mid-layer, and definitions from `a100u2w.h`. It exposes a PCI ID for `PCI_VENDOR_ID_INIT` device `0x1060`. Integration with hardware is through mailbox registers (`ORC_HDATA`, `ORC_HCTRL`, `ORC_HSTUS`), posting/reply queues (`ORC_PQUEUE`, `ORC_RQUEUE`), firmware SRAM/BIOS ports, and coherent DMA structures shared with the controller firmware.

## Risks

- The SCB and SG DMA addresses are truncated to 32 bits in hardware structures. The probe enforces a 32-bit DMA mask, but future structure changes must preserve that assumption.
- `orc_reset_scsi_bus()` holds `allocation_lock` with interrupts disabled while waiting up to roughly one second; this is explicitly called out in a FIXME.
- `orc_device_reset()` clears the allocation map before issuing the reset SCB and has an in-source FIXME about races with completion or reset issue failure.
- `inia100_build_scb()` maps DMA before some later SCB fields are fully consumed; failures after mapping must continue to unmap correctly.
- Sense data handling copies only `SENSE_SIZE` bytes and reuses the extended SG list storage as the sense buffer address.
- Firmware mailbox waits are fixed retry loops and can fail slowly or behave poorly if hardware is partially wedged.
- NVRAM default rewrite is automatic on invalid checksum/read failure, which is stateful hardware mutation.

## Test Signals

Signals include successful PCI probe and scan, correct firmware revision/readiness behavior, valid NVRAM checksum recovery, SCB allocation exhaustion returning `SCSI_MLQUEUE_HOST_BUSY`, SG mapping for zero and multi-entry commands, reply queue draining of multiple completions per interrupt, check-condition sense copying, abort success/failure paths, device reset SCB posting, bus reset recovery, and remove-path freeing of IRQ, coherent memory, I/O region, and SCSI host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a100u2w.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a100u2w.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/a100u2w.h

## Purpose

`a100u2w.h` defines the Initio/Orchid controller interface used by `a100u2w.c`: queue sizes, firmware mailbox commands, I/O register offsets, SCB and extended SCB layouts, SG descriptors, host adapter state, NVRAM layout, status codes, feature flags, and target configuration constants.

## Important APIs, Types, and Functions

- `inia100_REVID` supplies the SCSI host template name string.
- Queue and transfer constants include `ORC_MAXQUEUE`, `ORC_MAXTAGS`, `TOTAL_SG_ENTRY`, `MAX_TARGETS`, `IMAX_CDB`, `SENSE_SIZE`, `MAX_CHANNELS`, and `ORC_MAX_SCBS`.
- `struct orc_sgent` is a 32-bit base/length SG element consumed by firmware.
- `struct orc_extended_scb` stores the SG list and a Linux `struct scsi_cmnd *` back-pointer.
- `struct orc_scb` is the 64-byte firmware command block with opcode, flags, target/lun, transfer length, SG address, host/target status, message/tag/CDB fields, index, sense address, and extended SCB pointer.
- `struct orc_host` is the driver's per-host state and allocation pool metadata.
- `struct orc_nvram` maps the 64-byte EEPROM configuration image, including adapter IDs, BIOS options, channel configs, target configs, and checksum.
- `ORC_CMD_*`, `ORC_*` register offsets, `SCF_*`, `HOST_*`, `TARGET_*`, `NCC_*`, and `NTC_*` constants define firmware and hardware protocol values.

## Control Flow

The header shapes the control flow in `a100u2w.c`. Probe initializes `struct orc_host`, programs SCB base registers using the SCB/ESCB layout, and reads `struct orc_nvram`. Command queueing fills `struct orc_scb` and the `orc_extended_scb.sglist`, posts `scbidx`, and later reconstructs the SCB pointer from the returned index. Reset and abort paths use `ORC_BUSDEVRST` or `ORC_CMD_ABORT_SCB` values defined here.

## State and Persistence Behavior

The header describes three state domains: driver runtime state in `struct orc_host`, per-command coherent DMA state in `struct orc_scb` and `struct orc_extended_scb`, and adapter-persistent configuration in `struct orc_nvram`. NVRAM fields can be rewritten by the `.c` file when defaults are restored. The SCB structures are shared memory with the firmware, so field widths and endian conversions are part of the ABI.

## Dependencies and Integration Points

The header assumes Linux integer types, SCSI command types, PCI/DMA types pulled in by the `.c` file, and firmware that understands the Orchid SCB layout. It is tightly integrated with the Initio A100 hardware register map and mailbox protocol. It also exposes target options such as tag enable, disconnect, spin-up, sync/wide negotiation suppression, LVDS, parity, and termination configuration.

## Risks

- Some structure comments imply fixed firmware offsets while C layout contains pointer-size-dependent fields; the `CONFIG_64BIT` conditional padding is part of that risk.
- `NBC_DEFAULT` references `NBC_ENABLE`, but the defined BIOS-enable constant in this file is `NBC_BIOSENABLE`; this macro is not used by the observed `.c` file but is a latent compile hazard if used later.
- Firmware-visible addresses are 32-bit fields, so they rely on the probe-time DMA mask.
- The SCB maximums (`ORC_MAXQUEUE` 245, `ORC_MAX_SCBS` 250) are close but not identical and require care when changing allocation logic.
- Several NVRAM and target feature definitions appear legacy and may not be validated by modern SCSI transport negotiation code.

## Test Signals

Compile-time tests should catch structure layout and macro issues on 32-bit and 64-bit builds. Runtime validation should confirm SCB indexes match coherent array offsets, SG entries have little-endian 32-bit values, NVRAM checksum offsets match the 64-byte image, and firmware accepts `ORC_EXECSCSI`, `ORC_BUSDEVRST`, and mailbox command values as defined.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a100u2w.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a2091.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/a2091.c

## Purpose

`a2091.c` is the Commodore A2091/A590 Zorro II SCSI driver wrapper around the shared `wd33c93` SCSI core. It handles Amiga/Zorro probing, memory-mapped register setup, IRQ filtering, and board-specific DMA setup/stop for the A2091 DMA engine.

## Important APIs, Types, and Functions

- `struct a2091_hostdata` embeds `struct WD33C93_hostdata`, board registers, and the DMA device pointer.
- `a2091_intr()` filters shared Amiga port interrupts using `ISTR` flags and calls `wd33c93_intr()` under `host_lock`.
- `dma_setup()` maps the current WD33C93 SCSI pointer buffer for DMA, handles the A2091 24-bit/address-alignment constraints, allocates and maps bounce buffers when needed, programs `CNTR` and `ACR`, and starts DMA through `ST_DMA`.
- `dma_stop()` disables interrupts, flushes read DMA, clears pending interrupt state, stops DMA, restores control bits, unmaps DMA, and copies/free bounce buffers.
- `a2091_scsi_template` wires the driver to `wd33c93_queuecommand`, `wd33c93_abort`, and `wd33c93_host_reset`.
- `a2091_probe()` and `a2091_remove()` implement Zorro device lifecycle.

## Control Flow

Probe enforces a 24-bit coherent DMA mask, reserves 256 bytes of Zorro memory, allocates a SCSI host with `a2091_hostdata`, sets the shared Amiga ports IRQ, maps registers with `ZTWO_VADDR()`, programs `DAWR_A2091`, and passes SASR/SCMD register pointers plus the DMA callbacks to `wd33c93_init()`. After requesting the shared IRQ and enabling DMA-mode interrupts in `CNTR`, it registers and scans the host.

At I/O time the WD33C93 core calls `dma_setup()` with the current command pointer and direction. If the mapped DMA address violates `A2091_XFER_MASK`, the driver falls back to a sector-rounded bounce buffer; writes are copied into the bounce buffer before mapping. If a direct or bounced address is acceptable, `ACR` receives the physical address and `ST_DMA` starts the transfer. On completion or stop, `dma_stop()` restores control state, flushes reads until `ISTR_FE_FLG`, unmaps the original or bounce mapping, and copies read data from the bounce buffer on successful status.

## State and Persistence Behavior

The driver maintains only runtime state. `a2091_hostdata.wh` stores shared WD33C93 transfer state, including bounce buffer pointer, bounce length, and DMA direction. `regs` points at the board register window, and `dev` is used for DMA mapping. No persistent media or firmware state is modified. Register state persists while the driver is loaded and is reset by writing `CNTR = 0` during remove.

## Dependencies and Integration Points

This file depends on Amiga-specific Zorro, interrupt, and hardware address APIs, Linux DMA mapping, the SCSI mid-layer, `wd33c93.h`, and `a2091.h`. It registers a `zorro_driver` for `ZORRO_PROD_CBM_A590_A2091_1` and `_2`. Integration with the generic SCSI core is delegated to `wd33c93_init()` and the `wd33c93_*` host template callbacks.

## Risks

- The DMA hardware can only reach acceptable low/aligned physical addresses, so bounce-buffer behavior is critical.
- If mapping the bounce buffer fails, the code returns PIO fallback but must avoid leaking the allocated bounce buffer; the visible failure path after bounce-map error does not free it before returning.
- The read-flush loop waits indefinitely for `ISTR_FE_FLG`; a wedged DMA engine can spin forever.
- `dma_stop()` copies from bounce buffer only when `status` is true, so the semantic meaning of that status argument from `wd33c93` must remain stable.
- Shared IRQ filtering must be precise because `IRQ_AMIGA_PORTS` is shared.

## Test Signals

Validation should cover Zorro probe/remove, IRQ filtering when unrelated Amiga port interrupts occur, direct DMA and bounce DMA for read/write commands, PIO fallback when mapping or bounce allocation fails, flush behavior on reads, correct DMA unmap length/direction, and host reset/abort delegated through the WD33C93 core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a2091.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a2091.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/a2091.h

## Purpose

`a2091.h` defines the memory-mapped register layout and bit constants for the Commodore A2091/A590 Zorro II SCSI controller. It also supplies default SCSI queue limits used by `a2091.c`.

## Important APIs, Types, and Functions

- `CMD_PER_LUN` defaults to 2 and `CAN_QUEUE` defaults to 16 when not supplied by the build.
- `A2091_XFER_MASK` encodes physical DMA address restrictions: addresses with high bits outside the reachable 24-bit range or low-bit misalignment cannot be used directly.
- `struct a2091_scsiregs` maps the board register window, including `ISTR`, `CNTR`, `WTC`, `ACR`, `DAWR`, WD33C93 `SASR`/`SCMD`, DMA start/stop, interrupt clear, and flush registers.
- `DAWR_A2091`, `CNTR_*`, and `ISTR_*` constants define DMA control and interrupt/status bits.

## Control Flow

The `.c` file writes `DAWR_A2091`, tests `ISTR` in the IRQ handler, programs `CNTR` for DMA mode, writes `ACR` before `ST_DMA`, polls `ISTR_FE_FLG` after `FLUSH`, writes `CINT`, and stops DMA through `SP_DMA`. The register layout in this header determines all of those accesses.

## State and Persistence Behavior

The header defines volatile hardware registers only. Their state exists in the board while powered and while the driver is active. The Linux driver maintains runtime mirrors in `WD33C93_hostdata`; this header has no standalone persistence.

## Dependencies and Integration Points

It includes Linux integer types and is consumed by the Amiga/Zorro A2091 driver. `SASR` and `SCMD` integrate the board with the WD33C93 core, while the remaining registers integrate with the board DMA controller.

## Risks

- The C struct must match the hardware register spacing exactly; padding mistakes would redirect volatile I/O.
- `volatile` register accesses do not provide all ordering guarantees on their own; the `.c` file has fewer explicit memory barriers than the A3000 variant.
- The broad `A2091_XFER_MASK` makes bounce handling common on systems with memory outside the controller's DMA range.

## Test Signals

Tests should confirm register offsets against hardware documentation or emulator traces, ensure interrupt bits match observed A2091 behavior, and exercise DMA setup with addresses that both pass and fail `A2091_XFER_MASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a2091.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a3000.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/a3000.c

## Purpose

`a3000.c` is the Amiga 3000 built-in SCSI driver wrapper for the shared `wd33c93` core. It registers as a platform driver, maps the board register window, provides A3000-specific DMA setup/stop callbacks, handles shared Amiga port interrupts, and delegates SCSI command processing to WD33C93 common code.

## Important APIs, Types, and Functions

- `struct a3000_hostdata` embeds `struct WD33C93_hostdata`, A3000 register pointer, and DMA device pointer.
- `a3000_intr()` checks `ISTR_INT_P` and `ISTR_INTS`, dispatching to `wd33c93_intr()` under `host_lock` or warning for unserviced SCSI interrupts.
- `dma_setup()` maps the current command buffer, handles alignment restrictions through `A3000_XFER_MASK`, optionally allocates a bounce buffer, programs `CNTR`/`ACR`, and starts DMA with memory barriers around hardware accesses.
- `dma_stop()` disables DMA interrupts, flushes read DMA with barriers, clears interrupts, stops DMA, restores control bits, unmaps DMA, and frees/copies bounce buffers.
- `amiga_a3000_scsi_template` delegates queueing and EH callbacks to WD33C93.
- `amiga_a3000_scsi_probe()` and `amiga_a3000_scsi_remove()` handle platform lifecycle.

## Control Flow

Probe enforces a 32-bit coherent DMA mask, obtains an MMIO resource, reserves it, allocates a SCSI host with private host data, sets `IRQ_AMIGA_PORTS`, maps registers through `ZTWO_VADDR()`, writes `DAWR_A3000`, and provides WD33C93 SASR/SCMD register pointers plus `dma_setup()` and `dma_stop()` to `wd33c93_init()`. It then requests the shared IRQ, enables DMA-mode interrupts, adds the host, stores driver data, and scans the bus.

During transfer setup, the WD33C93 core passes the current SCSI pointer and direction. `dma_setup()` maps the buffer and warns if the DMA address fails the A3000 alignment mask. It allocates a sector-rounded bounce buffer when needed and copies write data into it. The function then programs direction, records `wh->dma_dir`, writes `CNTR`, sets the physical address in `ACR`, and starts DMA via `ST_DMA` with barriers. `dma_stop()` reverses this sequence, flushing read data if required, stopping DMA, restoring `CNTR`, unmapping the DMA address, and copying/freeing bounce state.

## State and Persistence Behavior

All state is runtime-only. The WD33C93 private data carries DMA direction and bounce buffer metadata; `a3000_hostdata` stores the register and device pointers. Register state is restored for active operation during probe and disabled by setting `CNTR = 0` during remove. There is no NVRAM or firmware persistence in this file.

## Dependencies and Integration Points

Dependencies include platform device resources, Amiga hardware/interrupt helpers, Linux DMA mapping, SCSI mid-layer headers, `wd33c93.h`, and `a3000.h`. It exposes `MODULE_ALIAS("platform:amiga-a3000-scsi")` and uses `module_platform_driver_probe()`, meaning runtime unbind is not expected and remove is marked through `__exit_p`.

## Risks

- The bounce-buffer path appears suspicious: after allocating and populating `wh->dma_bounce_buffer`, the code maps `scsi_pointer->ptr` again rather than `wh->dma_bounce_buffer`. That undermines the intended alignment fix and may be a latent bug.
- On bounce-map failure after allocation, the allocated bounce buffer is not freed before returning.
- The read flush waits indefinitely on `ISTR_FE_FLG`; hardware failure can spin.
- `dma_stop()` has redundant `SCpnt` checks and copies only when `status` is true; it depends on WD33C93 callback semantics.
- Platform driver registration via `module_platform_driver_probe()` means normal hot-unbind assumptions differ from many modern platform drivers.

## Test Signals

Signals include platform resource discovery, host scan, unrelated shared IRQ filtering, unserviced interrupt warnings, direct DMA and forced bounce paths, memory barrier-sensitive DMA ordering, read flush completion, PIO fallback on mapping/allocation failure, and remove cleanup of IRQ, host, and memory region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a3000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a3000.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/a3000.h

## Purpose

`a3000.h` defines the Amiga 3000 built-in SCSI DMA/register interface consumed by `a3000.c`. It provides queue defaults, DMA alignment mask, register layout, and control/status bit definitions.

## Important APIs, Types, and Functions

- `CMD_PER_LUN` and `CAN_QUEUE` default to 2 and 16.
- `A3000_XFER_MASK` requires DMA addresses to be 4-byte aligned.
- `struct a3000_scsiregs` maps DAWR, WTC, CNTR, ACR, DMA start, flush, interrupt clear, interrupt status, DMA stop, and WD33C93 `SASR`/`SCMD` registers.
- `DAWR_A3000` and `CNTR_*` values define board control programming.
- `ISTR_*` values define interrupt and FIFO status bits.

## Control Flow

The A3000 driver writes `DAWR_A3000` during probe, checks `ISTR_INT_P` and `ISTR_INTS` in the IRQ path, programs `CNTR` and `ACR` before `ST_DMA`, flushes reads through `FLUSH` plus `ISTR_FE_FLG`, clears interrupts via `CINT`, and stops DMA through `SP_DMA`. WD33C93 access is routed through `SASR` and `SCMD`.

## State and Persistence Behavior

The header declares volatile board registers and constants; persistence is limited to hardware register state while the device is active. It does not define any nonvolatile storage or long-lived software state.

## Dependencies and Integration Points

It includes Linux integer types and is tightly coupled to `a3000.c` and the WD33C93 core. The register struct is an ABI with the Amiga 3000 SCSI hardware mapped through the Zorro II address space.

## Risks

- Register padding must exactly match the hardware layout.
- `A3000_XFER_MASK` only captures alignment; any additional DMA boundary limitations must be enforced elsewhere.
- The header uses volatile fields, but safe ordering still depends on explicit barriers in the `.c` file.

## Test Signals

Validation should compare struct offsets with hardware documentation, exercise addresses failing and passing `A3000_XFER_MASK`, verify interrupt bits from emulator or hardware traces, and confirm the WD33C93 core can access `SASR` and `SCMD` through the mapped struct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a3000.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a4000t.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/a4000t.c

## Purpose

`a4000t.c` is the platform driver for the Amiga Technologies A4000T built-in NCR53C710 SCSI controller. It is a thin board wrapper around the generic `53c700` SCSI driver, providing platform resource mapping, host parameter initialization, IRQ registration, scanning, and cleanup.

## Important APIs, Types, and Functions

- `a4000t_scsi_driver_template` supplies SCSI host template identity fields: driver name, proc name, host ID 7, and module owner.
- `A4000T_SCSI_OFFSET` defines the offset from the platform memory resource to the NCR53C710 register block.
- `amiga_a4000t_scsi_probe()` allocates `NCR_700_Host_Parameters`, fills board-specific fields, calls `NCR_700_detect()`, requests the shared Amiga SCSI IRQ, stores platform data, and scans the host.
- `amiga_a4000t_scsi_remove()` removes the SCSI host, releases the generic NCR700 host, frees host parameters, releases IRQ and memory resources.
- `amiga_a4000t_scsi_driver` is registered with `module_platform_driver_probe()`.

## Control Flow

Probe obtains the memory resource, reserves it, allocates zeroed NCR700 host parameters, computes `scsi_addr = res->start + A4000T_SCSI_OFFSET`, maps the base through `ZTWO_VADDR()`, and sets `clock = 50`, `chip710 = 1`, `dmode_extra = DMODE_FC2`, and `dcntl_extra = EA_710`. It then calls `NCR_700_detect()` to create and initialize the SCSI host. On success it sets host ID, base, IRQ, requests `NCR_700_intr` on `IRQ_AMIGA_PORTS`, stores the host in platform data, and starts scanning.

Failure unwinds in reverse order: put SCSI host, free hostdata, and release memory region. Removal calls `scsi_remove_host()`, `NCR_700_release()`, frees the hostdata allocation, frees the IRQ, and releases the reserved region.

## State and Persistence Behavior

The file stores runtime state in the generic `Scsi_Host` and `NCR_700_Host_Parameters` allocated at probe. There is no persistent configuration or firmware mutation. Hardware register state is managed by the generic 53c700 core after detection and is released during remove.

## Dependencies and Integration Points

Dependencies include platform devices, Amiga hardware/interrupt definitions, SCSI host and SPI transport headers, and `53c700.h`. The driver exposes `MODULE_ALIAS("platform:amiga-a4000t-scsi")` and integrates with the generic NCR700 core through `NCR_700_detect()`, `NCR_700_intr`, and `NCR_700_release()`.

## Risks

- Resource mapping assumes the SCSI register block begins at `A4000T_SCSI_OFFSET` inside the platform resource.
- `kzalloc_obj()` is used for host parameters; any kernel-version compatibility issue with that helper would break build portability.
- The IRQ is shared on `IRQ_AMIGA_PORTS`; correctness depends on `NCR_700_intr` filtering unrelated interrupts.
- Because the driver uses `module_platform_driver_probe()`, the remove path is in exit text and normal runtime unbind is not expected.

## Test Signals

Signals include platform alias autoload, resource reservation, successful `NCR_700_detect()` with chip710 settings, shared IRQ request and interrupt filtering through the generic handler, SCSI bus scan, and cleanup of host, NCR700 resources, IRQ, hostdata, and memory region on module exit or probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/a4000t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/Makefile -->
# sources/distributed-fs/ceph-client/drivers/scsi/aacraid/Makefile

## Purpose

`aacraid/Makefile` declares how the kernel build system builds the Adaptec AACRAID SCSI driver. It is a Kbuild fragment rather than executable C code.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_SCSI_AACRAID) := aacraid.o` builds the `aacraid` driver object when the `CONFIG_SCSI_AACRAID` Kconfig option is enabled.
- `aacraid-objs := ...` lists the component objects linked into `aacraid.o`: `linit.o`, `aachba.o`, `commctrl.o`, `comminit.o`, `commsup.o`, `dpcsup.o`, `rx.o`, `sa.o`, `rkt.o`, `nark.o`, and `src.o`.

## Control Flow

There is no runtime control flow. At build time, Kbuild evaluates `CONFIG_SCSI_AACRAID`; when enabled, it compiles the listed source files and links them into one composite driver object named `aacraid.o`.

## State and Persistence Behavior

The file has no runtime state and no persistence. Its only state-like role is build graph declaration: changing the object list changes which source files participate in the driver binary.

## Dependencies and Integration Points

This Makefile integrates with Linux Kbuild and the `CONFIG_SCSI_AACRAID` Kconfig symbol. It assumes the listed `.c` files exist in the same `aacraid` directory and define the driver initialization, adapter communication, hardware-family support, and command paths.

## Risks

- Omitting a required object can produce link errors or missing hardware support.
- Adding object files in the wrong order is usually safe for linked C objects, but initcall/module symbol dependencies must still resolve.
- The build is gated entirely by `CONFIG_SCSI_AACRAID`; Kconfig dependency mistakes would prevent this Makefile from being reached.

## Test Signals

Build validation should include `CONFIG_SCSI_AACRAID=m` and `=y` configurations, clean builds that compile every listed component, module link success for `aacraid.o`, and modpost checks for exported symbols and license metadata from the component sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/aacraid/Makefile -->
