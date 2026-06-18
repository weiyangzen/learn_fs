# sources/distributed-fs/ceph-client/drivers/scsi/advansys.c lines 1-8605

## Scope

This chunk covers the front and middle of the Linux `advansys` SCSI host adapter driver. It includes the driver identity, narrow-board ASC constants and data structures, wide-board ADV constants and data structures, debug/procfs reporting helpers, command completion callbacks, narrow and wide firmware/microcode loading, chip reset/init helpers, interrupt paths, SCSI device configuration, request construction, and queue submission. The assigned range ends inside `AscInitAscDvcVar()` after the initial halt/status writes, so later EEPROM/probe/module registration code is outside this chunk.

## Purpose

`advansys.c` supports AdvanSys/ConnectCom SCSI host adapters through two related hardware paths:

- Narrow ASC boards use I/O-port access, ASC queue records in chip local RAM, an external firmware image `advansys/mcode.bin`, 8 target IDs, and 12-byte CDB support.
- Wide ADV boards use memory-mapped I/O, carrier rings, `ADV_SCSI_REQ_Q` request records, compressed firmware images for ASC-3550/38C0800/38C1600 chips, 16 target IDs, and 16-byte CDB support.
- Shared Linux SCSI glue translates `struct scsi_cmnd` into chip-specific request formats, handles queuecommand, device configuration, reset, interrupts, completions, residual counts, sense-buffer DMA, and `/proc/scsi/advansys/*` reporting.

The driver is hardware-contract heavy. Many structures are laid out to match firmware/microcode-visible local RAM formats, and the comments warn that several fields and byte orders must not change without matching microcode changes.

## Important Types And Constants

- `ASC_SCSIQ_*`, `ASC_QDONE_INFO`, `ASC_SG_HEAD`, `ASC_SCSI_Q`, `ASC_RISC_Q`, and `ASC_RISC_SG_LIST_Q`: narrow-board request, completion, and scatter-gather formats copied into or read from ASC local RAM.
- `ASC_DVC_CFG` and `ASC_DVC_VAR`: narrow-board static configuration and mutable adapter state. Runtime fields track `init_sdtr`, `sdtr_done`, tagged-queue masks, per-target queue depths, current queue counts, overrun DMA buffer state, interrupt/critical-section guards, firmware version/date, and bug-workaround masks.
- `ASCEEP_CONFIG`: narrow EEPROM layout, including chip SCSI ID, queue depth, SDTR/disconnect/tagging/start-motor masks, BIOS options, adapter info, and checksum.
- `ADVEEP_3550_CONFIG`, `ADVEEP_38C0800_CONFIG`, and `ADVEEP_38C1600_CONFIG`: wide EEPROM layouts for the three supported chip families, including termination, WDTR/SDTR/tagging, BIOS, serial, and error fields.
- `ADV_CARR_T`: firmware-visible carrier entry used to link wide-board command and response queues. The low bits of `next_vpa` carry done/good flags and must be masked with `ADV_NEXT_VPA_MASK`.
- `ADV_SCSI_REQ_Q`: wide-board firmware request/completion structure. The first 60 bytes are microcode-owned layout, little-endian, and include CDB, DMA addresses, status, residual/data count, SG pointer, carrier pointer, and tag.
- `adv_req_t` and `adv_sgblk_t`: Linux-side wrappers around wide requests and SG blocks, aligned for DMA. `adv_req_t` is indexed by block request tag and linked to `scsi_cmnd::host_scribble`.
- `struct asc_board`: per-host private state behind `shost_priv()`. It contains the narrow/wide unions, EEPROM union, per-target accounting, queue-full history, optional stats, narrow SDTR data, wide MMIO mapping, request pool, DMA pool, and BIOS metadata.
- `struct advansys_cmd`: per-command private storage for narrow sense-buffer DMA handle, reached through `scsi_cmd_priv()`.

Key constant groups define SCSI queue states (`QS_*`, `QC_*`, `QD_*`, `QHSTA_*`), local RAM variable addresses (`ASCV_*`, `ASC_MC_*`), I/O register offsets (`IOP_*`, `IOPB_*`, `IOPW_*`, `IOPDW_*`), EEPROM flags, chip IDs, termination and cable-detect masks, firmware idle commands, and microcode error/warning codes.

## Important Functions And APIs

- `advansys_info()` builds the one-line host description used by SCSI/proc reporting. It distinguishes narrow VL/EISA/PCI/PCI Ultra and wide Ultra-Wide/Ultra2-Wide/Ultra3-Wide adapters.
- `advansys_show_info()` and helpers such as `asc_prt_board_devices()`, `asc_prt_*_board_eeprom()`, `asc_prt_driver_conf()`, `asc_prt_*_board_info()`, and `asc_prt_board_stats()` expose board, EEPROM, target, transfer-mode, queue, and stats state through procfs when enabled.
- `AscStartChip()`, `AscStopChip()`, `AscResetChipAndScsiBus()`, `AscFindSignature()`, `AscEnableInterrupt()`, `AscDisableInterrupt()`, and `Asc*Lram*()` are narrow chip control/local-RAM access primitives.
- `AscLoadMicroCode()`, `AscInitLram()`, `AscInitQLinkVar()`, `AscInitMicroCodeVar()`, and `AscInitAsc1000Driver()` load `advansys/mcode.bin`, initialize ASC local RAM queues and firmware variables, map the overrun buffer, set the firmware PC, start the chip, and enable interrupts.
- `AdvLoadMicrocode()` expands compressed wide firmware images and verifies checksums. `AdvInitAsc3550Driver()`, `AdvInitAsc38C0800Driver()`, and `AdvInitAsc38C1600Driver()` load chip-specific firmware, restore BIOS LRAM state, configure DMA/FIFO/termination/selection masks, build carrier queues, start RISC execution, and optionally reset the SCSI bus.
- `AdvBuildCarrierFreelist()`, `adv_get_next_carrier()`, and `adv_get_reqp()` manage wide-board carrier and request lookup by firmware offsets.
- `AdvSendIdleCmd()`, `AdvResetSB()`, and `AdvResetChipAndSB()` send firmware idle commands for reset/abort-like operations and rebuild chip state during recovery.
- `advansys_interrupt()` is the top-level IRQ handler. It takes `shost->host_lock`, dispatches to `AscISR()` or `AdvISR()`, updates stats, and returns `IRQ_HANDLED` only when the adapter reports work.
- `AscISR()`, `AscIsrChipHalted()`, `AscIsrQDone()`, and `asc_isr_callback()` process narrow interrupts, SDTR/halt negotiations, done queues, queue-full adaptation, residuals, host/status bytes, and command completion.
- `AdvISR()`, `adv_async_callback()`, and `adv_isr_callback()` process wide interrupt status, async firmware events, response carriers, request lookup, status translation, sense/data DMA unmapping, target discovery, command completion, and SG block cleanup.
- `advansys_sdev_configure()` calls narrow/wide device configuration helpers. Narrow configuration updates SDTR and tagged queue masks; wide configuration enables WDTR, SDTR, PPR, and tag queueing in firmware local RAM based on inquiry-derived `scsi_device` capabilities and EEPROM masks.
- `asc_build_req()` and `adv_build_req()` translate `struct scsi_cmnd` into narrow `ASC_SCSI_Q` or wide `ADV_SCSI_REQ_Q`, map sense buffers and data SG lists, set CDB/tag/target fields, and populate little-endian DMA fields.
- `AscExeScsiQueue()` and `AdvExeScsiQueue()` submit requests to firmware. Narrow submission allocates local RAM queue slots and optional SG queue records; wide submission allocates a carrier, links it into the ICQ, and tickles/writes the chip notification register.
- `asc_execute_scsi_cmnd()` is the shared execution wrapper. `advansys_queuecommand_lck()` maps `ASC_BUSY` to `SCSI_MLQUEUE_HOST_BUSY` and completes commands immediately on hard request-building/execution errors.
- `advansys_reset()` runs SCSI error-handler reset logic by reinitializing the narrow chip or calling `AdvResetChipAndSB()` for wide boards, then drains wide completions through `AdvISR()`.
- `advansys_biosparam()` reports legacy disk geometry, using extended translation if the relevant BIOS flag is set and capacity exceeds 1 GB.

## Control Flow

For normal I/O, the SCSI midlayer calls `advansys_queuecommand_lck()`. The driver increments queuecommand stats and calls `asc_execute_scsi_cmnd()`. Narrow boards build a stack `ASC_SCSI_Q`, map the sense buffer into `advansys_cmd(scp)->dma_handle`, map the data SG list with `scsi_dma_map()`, optionally allocate a temporary `ASC_SG_HEAD`, and call `AscExeScsiQueue()`. Wide boards use the request tag as an index into `boardp->adv_reqp`, set `scp->host_scribble`, map the sense buffer, map/scatter the SG list into DMA-pool `adv_sgblk_t` blocks, and call `AdvExeScsiQueue()`.

Narrow submission checks adapter error state and critical-section reentry, calculates how many firmware queue slots are needed, applies old-chip bug workarounds, may issue SDTR message-out for pending negotiation, verifies per-target and total queue limits, writes CDB/request/SG records into local RAM, marks the queue `QS_READY`, advances the firmware free queue head, and updates `cur_total_qng` and `cur_dvc_qng`.

Wide submission verifies the target ID, gets a free carrier, stores the request tag and DMA address in firmware-visible fields, links the previous ICQ stopper to the new carrier's physical address, advances the stopper pointer, and notifies firmware. ASC-3550/38C0800 use the tickle byte; ASC38C1600 writes the COMMA register.

On interrupt, `advansys_interrupt()` serializes under the host lock. `AscISR()` first checks pending status, guards against unloaded microcode and ISR/critical reentry, acknowledges the interrupt, handles halted-chip negotiation cases, then drains one or multiple done queues depending on `ASC_CNTL_INT_MULTI_Q`. `AscIsrQDone()` copies completion state from local RAM, frees SG queue entries, updates queue counters, adjusts queue-full throttling, handles false-overrun and hung-bus-reset cases, and calls `asc_isr_callback()` unless callbacks were suppressed.

`AdvISR()` reads and clears the wide interrupt status. For async `INTRB`, it reads `ASC_MC_INTRB_CODE`, may tickle carrier-ready retry handling, and calls `adv_async_callback()`. It then walks completed IRQ carriers while `ADV_RQ_DONE` is set, maps the firmware request offset back to `adv_req_t`, synthesizes good status for `ADV_RQ_GOOD`, frees the previous stopper carrier back to the freelist, decrements pending count, clears request control, and calls `adv_isr_callback()`.

Both completion callbacks find the `scsi_cmnd` by tag, unmap sense DMA, translate chip `done_status`/`host_status`/`scsi_status` into Linux SCSI result fields, set residual bytes on underrun, mark target presence in `init_tidmask` on successful first completion, call `asc_scsi_done()`, and release wide SG DMA-pool blocks where applicable.

Initialization in this chunk is split by hardware. Narrow initialization resets the chip/SCSI bus if configured, verifies the ASC signature, disables interrupts, initializes queue local RAM, requests `advansys/mcode.bin`, validates a stored checksum prefix, writes firmware, maps an overrun buffer, writes microcode variables, starts at `ASC_MCODE_START_ADDR`, and enables interrupts. Wide initialization for all three chip families requests a chip-specific firmware image, expands it, verifies checksum, restores BIOS local RAM, writes microcode checksum/version/type variables, configures parity/DMA/termination/cable policy, initializes carrier queues and RISC queue pointers, enables interrupts, starts the RISC, and either restores BIOS-negotiated per-target state or resets the SCSI bus.

## State And Persistence Behavior

Persistent runtime state is per `Scsi_Host` in `struct asc_board` plus hardware local RAM/register state. Narrow mutable state includes queue heads/tails in local RAM, current total and per-target queue counts, SDTR done/init masks, tagged queue masks, queue-full throttling masks, and the DMA address of the overrun buffer. Wide mutable state includes firmware local RAM variables for WDTR/SDTR/PPR/tagging, the ICQ/IRQ carrier rings, pending-carrier count, per-target max-command bytes, and the preallocated request array indexed by block tags.

The firmware images are not embedded. They are requested at runtime from `advansys/mcode.bin`, `advansys/3550.bin`, `advansys/38C0800.bin`, or `advansys/38C1600.bin`. Their effects persist in adapter local RAM until reset/reinitialization. Wide initialization deliberately preserves and restores BIOS local RAM and per-target negotiated settings when a BIOS signature is present.

DMA state has several lifetimes:

- Narrow sense-buffer DMA is stored in `struct advansys_cmd` and unmapped in `asc_isr_callback()`.
- Narrow data SG DMA is mapped in `asc_build_req()` and unmapped by `asc_scsi_done()`.
- Narrow overrun DMA is mapped during microcode init and retained in `ASC_DVC_VAR`.
- Wide sense-buffer DMA is stored in `ADV_SCSI_REQ_Q::sense_addr` and unmapped in `adv_isr_callback()`.
- Wide data SG DMA is mapped by `scsi_dma_map()` and unmapped by `asc_scsi_done()`.
- Wide SG descriptor blocks are allocated per request from `boardp->adv_sgblk_pool` and freed after callback completion.
- Wide carriers and request arrays are host-lifetime structures; carrier entries cycle between ICQ/IRQ stopper lists and the freelist.

The procfs and stats data are observational. `ADVANSYS_STATS` is enabled in this file, so counters in `struct asc_stats` accumulate queuecommand, reset, biosparam, interrupt, callback, completion, build, execution, and transfer metrics while the host exists.

## Dependencies And Integration Points

- Linux SCSI midlayer: `struct Scsi_Host`, `struct scsi_cmnd`, `struct scsi_device`, `DEF_SCSI_QCMD`, `scsi_done()`, `scsi_change_queue_depth()`, `scsi_host_find_tag()`, SCSI status helpers, and EH reset entry points.
- Block layer tags: `scsi_cmd_to_rq(scp)->tag` is used as the firmware tag or tag+1 for narrow boards, and as the wide request array index.
- DMA APIs: `dma_map_single()`, `dma_unmap_single()`, `scsi_dma_map()`, `scsi_dma_unmap()`, `dma_pool_alloc()`, and `dma_pool_free()`.
- Firmware loader: `request_firmware()` and `release_firmware()` provide all microcode images.
- Port/MMIO access: narrow boards use `inb/outb/inw/outw`; wide boards use `readb/readw/writel` through `void __iomem *`.
- PCI integration: wide ASC38C1600 termination handling checks `PCI_FUNC(pdev->devfn)`, and `adv_dvc_to_pdev()` assumes wide boards are PCI-backed.
- Procfs/seq_file: optional reporting is guarded by `CONFIG_PROC_FS`.
- Kernel timing and locking: reset and firmware idle commands use `udelay()`/`mdelay()`, and interrupt handling uses `shost->host_lock`.
- SCSI protocol negotiation: configuration relies on `sdev->wdtr`, `sdev->sdtr`, `sdev->ppr`, and `sdev->tagged_supported`, plus SCSI CDB/status constants and extended-message codes.

## Risks And Edge Cases

- Firmware availability is required. Missing or too-short firmware images fail initialization or reset paths with microcode checksum errors.
- Several command-build error paths map one resource and then return busy/error after a later mapping failure. Reviewers should verify cleanup symmetry, especially sense-buffer DMA after `scsi_dma_map()` failure and wide sense mapping after SG-map failure.
- `advansys_info()` uses a static buffer and the file comments note it is unsafe for simultaneous callers. The code uses `sprintf()` followed by a `BUG_ON(strlen(info) >= ASC_INFO_SIZE)`, so an unexpectedly long address/range string would be caught only after writing.
- The carrier freelist builder has an `if (i == carr_num)` condition inside a loop bounded by `i < carr_num`; that condition is unreachable. The practical terminator behavior is handled elsewhere by reserving carrier 0 and stopper writes, but this is a maintenance hazard.
- Firmware-visible structures are layout and endian sensitive. Changing padding, alignment, or field order in `ADV_SCSI_REQ_Q`, `ADV_CARR_T`, or ASC queue structs can corrupt DMA/microcode contracts.
- Narrow local RAM queue management has explicit critical-section and ISR reentry guards. Any future call path into queue submission or ISR code must preserve host-lock/serialization assumptions.
- Queue-full handling dynamically lowers per-target queue depth for narrow boards on `SAM_STAT_TASK_SET_FULL`. This protects devices but can reduce concurrency persistently for that host session.
- The old narrow asynchronous/synchronous transfer workaround mutates SDTR registers based on device type, command, and transfer length. It is fragile and device-quirk driven.
- Reset routines use long `mdelay()` calls, including `scsi_reset_wait * 1000`, and therefore can stall the reset thread for substantial time.
- `AscIsrQDone()` contains a comment that `false_overrun` is always false, leaving an apparent dead branch in overrun handling.
- The assigned range ends before the rest of `AscInitAscDvcVar()` and before probe/remove/module registration, so full adapter discovery, resource allocation, and cleanup behavior must be covered by later chunks.

## Test Signals

- Build the driver with warnings enabled to catch structure-size, endian, format-string, and unreachable-code issues in this hardware-facing C file.
- Probe narrow and wide adapters with firmware files present and absent; expected logs should distinguish firmware load failure, bogus image length, checksum failure, bad chip signature, BIST errors, cable/termination errors, and successful initialization.
- Exercise queuecommand on zero-length, single-SG, multi-SG, and maximum-SG commands. Confirm `ASC_BUSY` returns `SCSI_MLQUEUE_HOST_BUSY`, hard errors complete with `DID_ERROR`, and successful commands complete once.
- Validate DMA cleanup with fault injection for `dma_map_single()`, `scsi_dma_map()`, `kzalloc_flex()`, `dma_pool_alloc()`, and carrier exhaustion.
- For interrupt tests, verify both narrow and wide completions unmap sense/data DMA, set residuals on underrun, preserve CHECK CONDITION sense data, and update `init_tidmask`.
- Test queue-full responses from targets and confirm narrow per-target queue limits are reduced and reported through procfs.
- Run SCSI bus reset/error-handler paths for narrow and all wide chip types, checking that firmware is reloaded, negotiated state is restored when BIOS state exists, and pending completions are drained.
- Inspect `/proc/scsi/advansys/*` on configured hosts for coherent EEPROM, BIOS, target, queue, transfer-mode, and stats output.
- Cover device negotiation combinations: no tag queueing, tag queueing, SDTR, WDTR, PPR on ASC38C1600, and warm-boot/no-bus-reset cases where EEPROM or BIOS-negotiated values are restored.
