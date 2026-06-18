# Research: sources/distributed-fs/ceph-client/drivers/scsi/advansys.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005226`: lines 1-8605, `Docs/researches/chunks/subset-b-005226_research.md`
- `subset-b-005227`: lines 8606-11554, `Docs/researches/chunks/subset-b-005227_research.md`

## Chunk Research

### subset-b-005226: lines 1-8605

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

### subset-b-005227: lines 8606-11554

# sources/distributed-fs/ceph-client/drivers/scsi/advansys.c lines 8606-11554

## Scope

This chunk covers the final hardware-configuration and driver-registration portion of the AdvanSys SCSI adapter driver. It starts near the end of narrow-board `ASC_DVC_VAR` default initialization, then implements narrow-board EEPROM access and recovery, wide-board EEPROM defaults/read/write/init mapping, the `scsi_host_template`, wide-board DMA memory setup, common board discovery, resource registration, SCSI host registration, adapter release, VLB/EISA/PCI bus probe and remove paths, and module init/exit.

The chunk is not standalone. It relies on the command execution, interrupt, reset, queueing, microcode loading, and SCSI command construction paths defined earlier in `advansys.c`, along with the type definitions for `ASC_DVC_VAR`, `ADV_DVC_VAR`, `ASCEEP_CONFIG`, the three `ADVEEP_*_CONFIG` layouts, and `struct asc_board`.

## Purpose

The code translates detected AdvanSys adapter hardware into a registered Linux SCSI host:

- Populate narrow-board defaults, read EEPROM state, repair invalid EEPROM data when possible, and apply chip-specific queueing, SCSI ID, synchronous transfer, termination, and PCI erratum settings.
- Provide equivalent EEPROM defaulting and field mapping for wide PCI chips: ASC-3550, ASC-38C0800, and ASC-38C1600.
- Allocate wide-board DMA-visible carrier/request/scatter-gather memory and start the appropriate wide microcode driver.
- Build the `Scsi_Host` limits from board capabilities: target count, LUN count, command length, queue depth, scatter-gather table size, BIOS address, IRQ, and host ID.
- Probe VLB, EISA, and PCI adapters, claim their I/O or PCI resources, create per-channel `Scsi_Host` objects, call the common board setup path, and unwind resources on failures.
- Register and unregister the ISA/VLB, EISA, and PCI bus drivers at module load/unload.

## Important APIs, Types, and Functions

Narrow-board initialization centers on `ASC_DVC_VAR`, `ASC_DVC_CFG`, and `ASCEEP_CONFIG`. `AscInitAscDvcVar()` has already initialized the early fields before this range and this chunk completes the default state: queue counters, busy queue heads/tails, `dvc_cntl`, reset delay, `start_motor`, maximum DMA count, default SDTR/disconnect masks, host SCSI ID, chip version, and SDTR period table. PCI Ultra chips switch `bus_type` to `ASC_IS_PCI_ULTRA`, use `asc_syn_ultra_xfer_period`, increase `max_sdtr_index`, and program extra SCSI control bits with `AscSetExtraControl()`.

Narrow EEPROM access uses `AscWriteEEPCmdReg()`, `AscWaitEEPRead()`, `AscReadEEPWord()`, `AscGetEEPConfig()`, `AscWriteEEPDataReg()`, `AscWriteEEPWord()`, `AscSetEEPConfigOnce()`, and `AscSetEEPConfig()`. These functions drive the chip EEPROM command/data registers through the earlier `AscSetChipEEPCmd()`, `AscGetChipEEPCmd()`, `AscSetChipEEPData()`, and `AscGetChipEEPData()` helpers. The read/write paths deliberately handle mixed byte/word fields in `ASCEEP_CONFIG` with `le16_to_cpu()` and `cpu_to_le16()` so byte fields read through 16-bit EEPROM operations land in the expected in-memory order.

`AscInitFromEEP()` is the narrow-board configuration bridge. It stops the chip and queue executor, optionally resets the SCSI bus, validates the microcode PC address, reads and normalizes chip config registers, reads EEPROM, handles checksum failures, tests external LRAM with `AscTestExternalLram()`, clamps queue limits, resolves command-queueing/disconnect conflicts, extracts the adapter SCSI ID, initializes per-target DOS INT13 and SDTR fields, and may rewrite EEPROM after checksum recovery.

`AscInitGetConfig()` and `AscInitSetConfig()` are the public narrow-board configuration stages called by board discovery. `AscInitGetConfig()` checks the signature, initializes defaults, imports EEPROM state, records init state bits, clamps reset wait, and logs warning/error codes. `AscInitSetConfig()` revalidates the signature, cleans config bits, forces disconnects when command queueing is enabled, handles PCI-specific config register clearing and old PCI errata flags, sets the chip SCSI ID for non-PCI paths, and logs warnings/errors.

Wide-board EEPROM support uses static defaults and field-classification tables:

- `Default_3550_EEPROM_Config` and `ADVEEP_3550_Config_Field_IsChar`.
- `Default_38C0800_EEPROM_Config` and `ADVEEP_38C0800_Config_Field_IsChar`.
- `Default_38C1600_EEPROM_Config` and `ADVEEP_38C1600_Config_Field_IsChar`.

`AdvWaitEEPCmd()` polls `IOPW_EE_CMD` for `ASC_EEP_CMD_DONE` and calls `BUG()` if the chip never completes. `AdvReadEEPWord()` issues an EEPROM read command. `AdvSet3550EEPConfig()`, `AdvSet38C0800EEPConfig()`, and `AdvSet38C1600EEPConfig()` write config words, compute the checksum over `ADV_EEP_DVC_CFG_BEGIN` to `ADV_EEP_DVC_CFG_END - 1`, write the checksum word, write the control/OEM area, and disable writes. `AdvGet3550EEPConfig()`, `AdvGet38C0800EEPConfig()`, and `AdvGet38C1600EEPConfig()` read the same EEPROM layouts and convert character-classified fields.

`AdvInitFrom3550EEP()`, `AdvInitFrom38C0800EEP()`, and `AdvInitFrom38C1600EEP()` map wide EEPROM state into `ADV_DVC_VAR` and `ADV_DVC_CFG`. They repair checksum failures by copying the matching default EEPROM image, preserving the serial-number words read from EEPROM, and rewriting the EEPROM. They clamp `max_host_qng` and `max_dvc_qng` to driver-supported ranges, derive SDTR ability for 38C0800/38C1600 chips from packed four-target speed nibbles, decode termination policy, and return non-fatal warning bits. The 38C1600 path also adjusts Function 1 defaults: disables expansion ROM BIOS and derives INT A/INT B wiring from GPIO bit 0.

`AdvInitGetConfig()` is the wide-board get-config entry point. It records the PCI command parity bit into `control_flag`, reads chip version, validates the wide signature and `chip_type`, resets the chip, enables register writes, and dispatches to the chip-specific EEPROM init function.

The Linux SCSI integration point is `advansys_template`, whose callbacks are `.info = advansys_info`, `.queuecommand = advansys_queuecommand`, `.eh_host_reset_handler = advansys_reset`, `.bios_param = advansys_biosparam`, `.sdev_configure = advansys_sdev_configure`, and `.cmd_size = sizeof(struct advansys_cmd)`. The actual command and interrupt behavior behind these callbacks is earlier in the file; this chunk wires them into hosts allocated by `scsi_host_alloc()`.

Common board setup is in `advansys_board_found()`. It fills either `boardp->dvc_var.asc_dvc_var` for narrow boards or `boardp->dvc_var.adv_dvc_var` for wide boards, maps wide PCI BAR 1 with `pci_ioremap_bar()`, calls `AscInitGetConfig()` or `AdvInitGetConfig()`, snapshots EEPROM-derived fields into `boardp->eep_config` for procfs reporting, sets `Scsi_Host` limits, requests the IRQ, initializes chip microcode, registers the host with `scsi_add_host()`, and starts scanning with `scsi_scan_host()`.

Wide runtime memory is managed by `advansys_wide_init_chip()` and `advansys_wide_free_mem()`. The init path allocates coherent carrier memory with `dma_alloc_coherent()`, coherent request memory sized from `max_host_qng`, and a DMA pool for `adv_sgblk_t` blocks, then calls `AdvInitAsc3550Driver()`, `AdvInitAsc38C0800Driver()`, or `AdvInitAsc38C1600Driver()`. The free path releases the coherent areas and DMA pool and nulls their pointers.

Bus integration is split across VLB/ISA, EISA, and PCI:

- `_asc_def_iop_base[]`, `advansys_vlb_irq_no()`, `advansys_vlb_probe()`, `advansys_vlb_remove()`, and `advansys_vlb_driver` handle legacy VLB adapters through `isa_register_driver()`.
- `advansys_eisa_table`, `struct eisa_scsi_data`, `advansys_eisa_irq_no()`, `advansys_eisa_probe()`, `advansys_eisa_remove()`, and `advansys_eisa_driver` handle one or two EISA channels per device.
- `advansys_pci_tbl`, `advansys_set_latency()`, `advansys_pci_probe()`, `advansys_pci_remove()`, and `advansys_pci_driver` handle supported PCI device IDs and flag ABP940UW/38C0800/38C1600 devices as wide boards.

## Control Flow

For a narrow board, probe enters from the relevant bus probe and calls `advansys_board_found()`. The board-private `ASC_DVC_VAR` points at its `ASC_DVC_CFG`, records the I/O port, and records the detected bus type. The IRQ sharing policy is selected from the bus type. `AscInitGetConfig()` then verifies the signature, initializes defaults, and calls `AscInitFromEEP()`.

`AscInitFromEEP()` first forces the chip into a safe stopped state. It writes a halt marker in LRAM, stops queue execution, stops or resets the chip/SCSI bus if required, and fails if the chip is not halted or the program counter cannot be set to `ASC_MCODE_START_ADDR`. It then reads chip config registers and clears bits that must not persist. EEPROM import reads the checksum-covered fields and final checksum word. Auto-config state can override EEPROM config-lsw/config-msw for old chip version 3 boards.

After EEPROM import, checksum mismatch has two paths. PCI Ultra 3050 EEPROM-less boards receive hardcoded defaults and an adapter-info marker `0xBB`. Other narrow boards set `write_eep`, warn, continue with the read buffer, and later call `AscSetEEPConfig()` to rewrite the EEPROM with normalized values. Queue counts are adjusted for boards without external LRAM, bounded to `ASC_MIN_TOTAL_QNG` and `ASC_MAX_TOTAL_QNG`, and per-device tag queueing is bounded between `ASC_MIN_TAG_Q_PER_DVC` and total queue depth. Command queueing forces disconnect enablement for matching targets, the host SCSI ID is masked to `ASC_MAX_TID`, Ultra boards without Ultra SDTR enabled use the 10 MB/s minimum SDTR index, and each target receives its default SDTR period/offset.

`AscInitSetConfig()` runs after the EEPROM snapshot is stored in `boardp->eep_config.asc_eep`. It re-clears config bits, repeats the queueing/disconnect consistency check, records auto-config warnings, and for PCI boards clears low config bits and marks old 1200A/ABP940 chips with `ASC_BUG_FIX_IF_NOT_DWB` and `ASC_BUG_FIX_ASYN_USE_SYN`. Non-PCI paths set the chip SCSI ID directly.

For a wide board, `advansys_board_found()` fills `ADV_DVC_VAR`, identifies the chip type from the PCI device ID, maps PCI BAR 1 for memory-mapped register access, saves the legacy I/O port for reporting, and calls `AdvInitGetConfig()`. That function samples PCI parity behavior, validates chip identity, resets the chip, allows register writes, and dispatches to the chip-specific EEPROM import. The chip-specific import either trusts the EEPROM checksum or loads defaults and rewrites EEPROM, then maps wide transfer, queue, termination, BIOS, SCSI ID, and serial fields into `ADV_DVC_VAR`.

After board-specific configuration, `advansys_board_found()` snapshots EEPROM-derived settings into the board-private `eep_config` union. Narrow boards store `init_sdtr`, `disc_enable`, `use_cmd_qng`, start-motor, control, no-SCAM, queue, SCSI ID, max tag queue, and adapter-info values. Wide boards store the fields relevant to their chip family, including termination, BIOS control, WDTR/SDTR or SDTR-speed words, tag queueing, start motor, reset delay, and serial number.

The common SCSI host setup then sets `max_channel = 0`, target/LUN limits, maximum command length, `io_port`, `this_id`, `can_queue`, and `sg_tablesize`. Narrow `sg_tablesize` is derived from available queue blocks and `ASC_SG_LIST_PER_Q`; wide boards use `ADV_MAX_SG_LIST`. The value is capped at `SG_ALL`. BIOS address is read either through `AscGetChipBiosAddress()` for narrow boards or from wide LRAM BIOS fields, with a valid `0x55AA` signature causing the x86 real-mode code segment to be shifted left four bits into `shost->base`.

IRQ registration happens before chip microcode initialization. If `request_irq()` fails, setup unwinds mapped wide memory and returns an error to the bus probe. Narrow boards allocate `overrun_buf`, then call `AscInitAsc1000Driver()`. An initialization warning/error is tolerated only if `overrun_dma` was set; otherwise setup fails. Wide boards call `advansys_wide_init_chip()`, which allocates DMA resources and starts the chip-specific wide driver. On success, the host is registered with `scsi_add_host()` and scanning starts.

Release flows reverse the successful setup path. `advansys_release()` removes the SCSI host, frees the IRQ, unmaps and frees narrow overrun DMA/buffer or wide MMIO/DMA resources, then drops the host reference with `scsi_host_put()`. Bus remove functions also release bus-owned I/O regions or PCI regions and disable the PCI device.

VLB probing iterates a fixed I/O-port table through the ISA driver core. It claims the I/O region, checks the narrow signature and VLB chip-version maximum, allocates a host, decodes the IRQ from CfgLsw bits 2:4, and calls `advansys_board_found()` with `ASC_IS_VL`.

EISA probing allocates `struct eisa_scsi_data`, starts at `base_addr + 0xc30`, and checks up to two channels separated by `0x20`. Each present channel claims an I/O region, verifies the signature, performs an unexplained `inw(ioport + 4)` compatibility read, decodes a shared IRQ from CfgLsw bits 8:10, allocates a host, and calls `advansys_board_found()` with `ASC_IS_EISA`. A successfully initialized channel is saved in `data->host[i]`; removal walks both hosts.

PCI probing enables the device, claims PCI regions, enables bus mastering, adjusts the latency timer, requires BAR 0 to be non-empty for the I/O port, allocates a host, stores IRQ/device pointers, marks wide boards by device ID, and calls `advansys_board_found()` with `ASC_IS_PCI`. Wide boards also require BAR 1 mapping inside the common setup path.

Module init registers the VLB/ISA driver first, then the EISA driver, then the PCI driver. Failures unwind previously registered bus drivers. Module exit unregisters in reverse bus order: PCI, EISA, then ISA.

## State and Persistence

The key persistent hardware state is EEPROM content. Both narrow and wide paths read EEPROM into typed config structures, compute checksums over defined word ranges, and may rewrite EEPROM when a checksum mismatch is found. Narrow non-EEPROM-less checksum failures trigger a rewrite after normalized values are applied. Wide checksum failures copy default EEPROM images, preserve serial-number words, and write the defaults back to the board. These rewrites outlive the driver and are the most durable side effect in this chunk.

Runtime state lives mostly in `struct asc_board`, allocated as SCSI host private data. It owns the `ASC_DVC_VAR` or `ADV_DVC_VAR`, matching config union, EEPROM snapshot union, IRQ, device pointer, host pointer, init target mask, queue bookkeeping, optional stats, narrow SDTR data, and wide MMIO/DMA resources. `advansys_board_found()` populates this state once at probe time and later code paths use it for queueing, interrupts, procfs reporting, device configuration, and release.

Narrow runtime state includes per-target queue counters and busy queue links, `cfg->sdtr_enable`, `cfg->disc_enable`, `cfg->cmd_qng_enabled`, per-target `cfg->max_tag_qng`, per-target `cfg->sdtr_period_offset`, `dos_int13_table`, `dvc_cntl`, `start_motor`, `no_scam`, `max_total_qng`, `min_sdtr_index`, and chip-specific bug-fix flags. The chunk also configures chip registers such as config MSW/LSW, extra control, host interrupt enablement via EEPROM cfg-lsw normalization, and SCSI ID.

Wide runtime state includes `chip_type`, memory-mapped `iop_base`, `control_flag`, chip version, transfer capability masks, packed SDTR speed words, queue limits, termination setting, BIOS control, SCSI ID, start motor, reset delay, no-SCAM flag, serial fields, coherent carrier/request memory, and the SG DMA pool. The 38C1600 EEPROM recovery path persists function-specific ROM and interrupt wiring policy in EEPROM defaults.

Linux-visible state is also persisted in `Scsi_Host`: queue depth, target/LUN limits, command length, SG table size, BIOS base, IRQ, host ID, I/O port, DMA channel marker, and callback table. Once `scsi_add_host()` and `scsi_scan_host()` succeed, the SCSI midlayer owns discovery and command dispatch through the callbacks wired in this chunk.

## Dependencies and Integration Points

This chunk depends on low-level register helpers and chip-control code defined earlier in the same file: narrow `Asc*` I/O helpers, wide `AdvRead*`/`AdvWrite*` register and LRAM macros, queue/microcode initialization (`AscInitAsc1000Driver()`, `AdvInitAsc3550Driver()`, `AdvInitAsc38C0800Driver()`, `AdvInitAsc38C1600Driver()`), interrupt handling (`advansys_interrupt`), reset handling (`advansys_reset`), command queueing (`advansys_queuecommand`), device configuration (`advansys_sdev_configure`), and BIOS geometry (`advansys_biosparam`).

Kernel subsystem integration points include:

- SCSI core: `scsi_host_alloc()`, `scsi_add_host()`, `scsi_scan_host()`, `scsi_remove_host()`, `scsi_host_put()`, `struct scsi_host_template`, and `struct Scsi_Host` limits.
- IRQ core: `request_irq()` and `free_irq()`, with VLB using non-shared IRQs and EISA/PCI using `IRQF_SHARED`.
- DMA API: `dma_alloc_coherent()`, `dma_free_coherent()`, `dma_pool_create()`, `dma_pool_destroy()`, `dma_unmap_single()`, and the narrow overrun buffer path initialized by earlier code.
- PCI core: `pci_enable_device()`, `pci_request_regions()`, `pci_set_master()`, `pci_ioremap_bar()`, `pci_read_config_word()`, `pci_read_config_byte()`, `pci_write_config_byte()`, `pci_set_drvdata()`, `pci_release_regions()`, and `pci_disable_device()`.
- ISA/VLB and EISA bus cores: `isa_register_driver()`, `isa_unregister_driver()`, `struct isa_driver`, `eisa_driver_register()`, `eisa_driver_unregister()`, `struct eisa_driver`, `MODULE_DEVICE_TABLE(eisa, ...)`, and EISA base-address probing.
- I/O resource management: `request_region()`, `release_region()`, port I/O (`inw()`, `inp()`, `inpw()`), and MMIO unmapping with `iounmap()`.
- Module and firmware metadata: `module_init()`, `module_exit()`, `MODULE_DEVICE_TABLE(pci, ...)`, `MODULE_DESCRIPTION`, `MODULE_LICENSE`, and `MODULE_FIRMWARE()` declarations for narrow and wide microcode blobs.

The procfs display path is an indirect integration point. This chunk snapshots EEPROM data into `boardp->eep_config` specifically so `/proc/scsi/advansys/[0...]` reporting code earlier in the file can show the board configuration.

## Risks and Edge Cases

- EEPROM rewrite is persistent and hardware-facing. Checksum recovery paths can modify adapter EEPROM during probe. A bad default table, wrong field endian marker, or incorrect checksum range would persist broken configuration beyond module unload.
- `AdvWaitEEPCmd()` calls `BUG()` if EEPROM command completion never appears. A wedged or absent EEPROM on a wide board can panic the kernel rather than failing probe gracefully.
- `AscTestExternalLram()` writes test pattern `0x55AA` to the queue address for queue number 241 and restores it only when the readback succeeds. If the write partially works but readback fails, the saved word is not restored.
- Several paths use busy waits with `mdelay()`, including narrow SCSI reset waits up to seconds and EEPROM write delays. Probe can block CPU time for legacy hardware operations.
- Narrow checksum mismatch recovery is asymmetric. EEPROM-less PCI Ultra 3050 boards get known defaults, but other checksum failures continue using the read buffer before rewrite. If the read buffer contains severe corruption, normalized bounds cover queue fields but not every policy field.
- Warning code handling in `AscInitGetConfig()` and `AscInitSetConfig()` uses a `switch` over exact warning values, but `warn_code` is a bitmask. Multiple simultaneous warning bits fall through to "unknown warning" instead of printing each constituent condition.
- The narrow PCI branch in `AscInitSetConfig()` does not call `AscSetChipScsiID()` because the `else` binds to the non-PCI case. Correctness depends on PCI chip SCSI ID being set by config register/EEPROM paths.
- `advansys_wide_init_chip()` reports all allocation failures as "kmalloc() failed" and does not immediately free any resources allocated before a later allocation failure. The caller's `err_free_mem` path calls `advansys_wide_free_mem()`, so this relies on the common unwind path being used.
- `advansys_release()` always calls `dma_unmap_single()` for narrow `overrun_dma`. If release were reached after a partially initialized narrow board without a valid mapping, this could be unsafe; normal successful probe initializes it through `AscInitAsc1000Driver()`.
- EISA failure cleanup uses `kfree(data->host[0])` and `kfree(data->host[1])` instead of `scsi_host_put()` for already allocated host structures on the final `free_data` path. This is suspicious because successful `scsi_host_alloc()` objects should be released through the SCSI host API.
- EISA channel probing breaks out after a failure following a present/signature-matching channel. Later possible channels are not tried after that point.
- VLB `advansys_vlb_irq_no()` and EISA `advansys_eisa_irq_no()` can return `0` for invalid encoded IRQs, but the later common path still attempts `request_irq(0, ...)`.
- Wide boards require PCI BAR 1 mapping. If BAR 0 is present but BAR 1 is absent or cannot be mapped, probe fails after the host has been allocated and must rely on the common/bus unwind paths.
- `advansys_set_latency()` forces old PCI chips to latency timer 0 and raises other chips to at least `0x20`; this is hardware-policy-sensitive and may interact with platform PCI quirks.
- Module init registers legacy ISA/VLB before EISA and PCI. A failure in later bus registration unwinds earlier registrations, but any already probed device side effects depend on bus-core unregister behavior.

## Test and Validation Signals

Useful validation signals for this chunk are mostly probe/remove and hardware-facing:

- Build coverage with `CONFIG_PCI`, EISA, and ISA/VLB combinations should catch compile-time gating around wide-board code and legacy bus drivers.
- PCI probe on supported IDs should show successful `pci_enable_device()`, region claim, bus mastering, latency setup, BAR 0 I/O presence, wide-board flagging for ABP940UW/38C0800/38C1600, and BAR 1 MMIO mapping for wide boards.
- Narrow probe should log a valid signature, EEPROM checksum result, chip version, bounded queue depth, SCSI ID, SG table size, successful IRQ request, `AscInitAsc1000Driver()` result, `scsi_add_host()` success, and scan start.
- Wide probe should log valid chip ID/signature, chip type, EEPROM checksum/default recovery status, queue limits, termination mapping, successful coherent carrier/request allocation, SG DMA pool creation, chip-specific `AdvInitAsc*Driver()` result, host registration, and scan start.
- EEPROM checksum injection or hardware with bad EEPROM should exercise default recovery and verify that serial-number words are preserved on wide boards, queue limits are sane, and warning reporting is understandable.
- Endianness-sensitive tests should verify that byte-classified EEPROM fields such as SCSI ID, reset delay, queue limits, termination bytes, and OEM name bytes read and write identically on big-endian and little-endian builds.
- LRAM-size tests should cover narrow boards with and without external LRAM, confirming fallback queue depths (`ASC_MAX_PCI_ULTRA_INRAM_TOTAL_QNG`, `ASC_MAX_PCI_INRAM_TOTAL_QNG`) and config MSW changes.
- IRQ error injection should confirm that `request_irq()` failures release MMIO mappings and bus-owned regions and that invalid VLB/EISA IRQ encodings do not leave claimed regions behind.
- DMA allocation failure injection for wide boards should verify that carrier, request, and SG pool resources are freed by `advansys_wide_free_mem()` through the common error path.
- `scsi_add_host()` failure injection should free IRQs, narrow overrun memory or wide DMA resources, and mapped MMIO.
- Remove/unload tests should verify `scsi_remove_host()`, IRQ freeing, DMA unmap/free, `iounmap()`, PCI region release, PCI disable, VLB/EISA `release_region()`, and final `scsi_host_put()`.
- EISA multi-channel hardware or emulation should validate that both channels can register independent `Scsi_Host` instances, share the decoded IRQ correctly, and remove cleanly.
- Runtime SCSI smoke tests after probe should include device discovery, tagged queueing/disconnect behavior, synchronous/wide transfer negotiation from EEPROM settings, host reset through the SCSI error-handler callback, and module unload under idle and after I/O error conditions.
