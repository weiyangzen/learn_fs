# Research: sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_core.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-005229`: lines 1-9380, `Docs/researches/chunks/subset-b-005229_research.md`
- `subset-b-005230`: lines 9381-10724, `Docs/researches/chunks/subset-b-005230_research.md`

## Chunk Research

### subset-b-005229: lines 1-9380

# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_core.c lines 1-9380

## Scope

This chunk covers the first 9,380 lines of the Adaptec AIC79xx Ultra320 SCSI core. It includes lookup tables, sequencer mode control, scatter/gather setup, SCB queuing, completion FIFO processing, interrupt handlers, packetized and non-packetized recovery, transfer negotiation, message phase handling, controller and SCB allocation, chip initialization, reset/suspend/resume paths, queue search/abort logic, status and residual handling, target-mode event queuing, and the beginning of sequencer program download. The range ends inside `ahd_loadseq()` while it is building and applying firmware patch/critical-section metadata; the patch predicate and instruction download helpers are outside this chunk.

## Purpose

`aic79xx_core.c` is the OS-shared core for the AIC7901/AIC7902 family. It bridges CAM/SCSI commands represented as SCBs to the adapter's downloaded sequencer firmware and hardware FIFOs. The chunk handles:

- Turning platform-allocated `struct scb` objects into hardware SCBs and scatter/gather lists that the adapter can DMA.
- Programming and restarting the sequencer, including mode switching across SCSI, command-channel, and data FIFO register banks.
- Servicing normal command completions through the host-visible QOUTFIFO and exceptional completions that require SCB DMA-back.
- Recovering from hardware, sequencer, SCSI, packetized L_Q, busfree, parity/CRC, protocol, selection timeout, overrun, and bus reset events.
- Negotiating parallel SCSI transfer parameters: width, sync period/offset, PPR options, packetized/IU/QAS/RTI/DT, and fallback to older SPI behavior.
- Allocating and freeing controller state, DMA-safe shared data, hardware SCBs, S/G lists, sense buffers, target-state tables, and target-mode event queues.
- Initializing chip registers, scratch RAM, FIFO state, command size tables, interrupt coalescing, and the downloaded sequencer program.

## Important APIs, Types, and Functions

- `struct ahd_softc` is the controller instance. This file mutates its mode cache, flags, bug/feature masks, interrupt-coalescing counters, pending SCB list, SCB pools, shared DMA memory, QIN/QOUT FIFO positions, message buffers, target tables, and sequencer patch metadata.
- `struct scb`, `struct hardware_scb`, and `struct scb_data` are the command resource model. A software SCB owns platform data, DMA maps, an HSCB, S/G memory, sense memory, tags, collision-list links, and active/recovery flags.
- `struct ahd_devinfo`, `struct ahd_initiator_tinfo`, `struct ahd_tmode_tstate`, and `struct ahd_transinfo` describe a nexus and its user/goal/current transfer settings.
- `ahd_set_modes()`, `ahd_save_modes()`, `ahd_restore_modes()`, `ahd_pause()`, and `ahd_unpause()` manage the chip's mode pointer and sequencer execution. Most register access in this chunk assumes the correct source/destination mode.
- `ahd_sg_setup()`, `ahd_setup_data_scb()`, `ahd_setup_noxfer_scb()`, `ahd_sync_scb()`, `ahd_sync_sglist()`, and `ahd_sync_sense()` prepare DMA-visible command, data, and sense state.
- `ahd_queue_scb()` swaps the incoming command onto the adapter-known `next_queued_hscb`, prepares data pointers, syncs the HSCB, records the tag in the software QINFIFO history, and advances `HNSCB_QOFF`.
- `ahd_intr()` is the primary interrupt entry point. It fast-paths command completion by checking the in-memory completion queues, then handles command-complete, hardware error, PCI/split, sequencer, and SCSI interrupts.
- `ahd_run_qoutfifo()` drains normal completions; `ahd_flush_qoutfifo()` manually drains good-status, DMA-back, complete-on-freeze, and complete-list SCBs when the chip is being paused or reset.
- `ahd_handle_seqint()` handles sequencer-reported events such as invalid sequencer interrupts, illegal phases, packetized status overrun, configuration-for-status/sense DMA, data overruns, host message loops, no-match reselections, protocol violations, task-management completion, and debug tracepoints.
- `ahd_handle_scsiint()`, `ahd_handle_transmission_error()`, `ahd_handle_lqiphase_error()`, `ahd_handle_pkt_busfree()`, and `ahd_handle_nonpkt_busfree()` are the SCSI-bus recovery core.
- `ahd_set_syncrate()`, `ahd_set_width()`, `ahd_find_syncrate()`, `ahd_devlimited_syncrate()`, `ahd_validate_offset()`, `ahd_validate_width()`, and `ahd_update_neg_table()` keep software negotiation state and the hardware negotiation table synchronized.
- `ahd_setup_initiator_msgout()`, `ahd_build_transfer_msg()`, `ahd_construct_sdtr()`, `ahd_construct_wdtr()`, `ahd_construct_ppr()`, `ahd_handle_message_phase()`, `ahd_parse_msg()`, and `ahd_handle_msg_reject()` implement manual SCSI message phase handling.
- `ahd_alloc()`, `ahd_free()`, `ahd_reset()`, `ahd_init()`, `ahd_chip_init()`, `ahd_default_config()`, `ahd_parse_cfgdata()`, `ahd_parse_vpddata()`, `ahd_suspend()`, and `ahd_resume()` are the controller lifecycle/configuration path used by platform-specific attach code.
- `ahd_get_scb()`, `ahd_free_scb()`, `ahd_alloc_scbs()`, `ahd_search_qinfifo()`, `ahd_search_scb_list()`, `ahd_abort_scbs()`, and `ahd_reset_channel()` manage SCB ownership, queues, resets, and abort completion.
- `ahd_handle_scsi_status()`, `ahd_handle_scb_status()`, and `ahd_calc_residual()` translate hardware status and residual fields into CAM/SCSI completion state and autosense requests.
- Under `AHD_TARGET_MODE`, `ahd_queue_lstate_event()` and `ahd_send_lstate_events()` queue bus-reset/message events for target-mode immediate notify CCBs.

## Control Flow

Attach begins with platform code allocating an `ahd_softc` through `ahd_alloc()`, filling PCI/platform details, and calling configuration helpers. If EEPROM data is not usable, `ahd_default_config()` sets ID 7, wide/sync/packetized-capable user goals, and conservative async/narrow current state. If EEPROM data exists, `ahd_parse_cfgdata()` imports target flags, disconnect/tag eligibility, transfer period, packetized/QAS options, parity, reset, BIOS, and termination flags.

`ahd_init()` probes the sequencer stack, allocates shared DMA memory for the QOUTFIFO, optional target command FIFO, packet overrun buffer, and sentinel `next_queued_hscb`, then initializes SCB DMA pools. It gives the platform layer a final chance to adjust settings, calls `ahd_chip_init()`, optionally runs flexport current-sensing termination diagnostics, restarts the sequencer, and starts the statistics timer.

`ahd_chip_init()` is the central hardware bring-up routine. It programs SCSI IDs, termination/parity/selection timeout controls, SCSI/LQI/LQO interrupt masks, data FIFO state, SCB field offsets, CDB length tables, negotiation table entries, queue heads/tails, busy-target table entries, shared-data bus addresses, coalescing registers, and sequencer vectors. It clears all software-visible queue positions, downloads `seqprog` through `ahd_loadseq()`, and applies chip-specific workarounds such as IOCELL bypass and slow CRC.

Normal I/O follows this path: the platform layer obtains an SCB with `ahd_get_scb()`, fills the HSCB and S/G list, and calls `ahd_queue_scb()`. The sequencer downloads HSCBs from the host queue, selects/reselects targets, transfers data, and writes completion entries into `qoutfifo`. `ahd_intr()` clears command-complete interrupts and calls `ahd_run_qoutfifo()`, which looks up each tag, dispatches either `ahd_done()` for good completions or `ahd_handle_scb_status()` when the hardware reports status/residual information, and advances the valid-tag ring.

Error and recovery paths pause or keep the sequencer paused, move it out of critical sections if needed, inspect chip status, update host-visible SCB state, and either unpause, restart, or reset the bus. Selection timeouts call `ahd_handle_devreset()` to abort matching work and reset transfer negotiation. Unexpected busfree handling differentiates packetized LQO failures, expected abort/reset/negotiation busfrees, expected IU-change busfrees, and real protocol loss. Severe or ambiguous failures reset the bus through `ahd_reset_channel()`.

Message handling starts when the sequencer emits `HOST_MSG_LOOP`. For initiator message-out, the core constructs identify/tag, abort, target reset, parity-error, or transfer-negotiation messages. For message-in, it parses incoming one-byte and extended messages, validates requested transfer settings against adapter and target limits, updates negotiation state, and optionally asserts ATN to send a response. Target-mode builds the equivalent message-in/out flow when compiled in.

Status processing freezes queues for non-good SCSI status, records CAM status, handles packetized status IU details, and issues autosense when requested. Autosense replaces the active SCB CDB with REQUEST SENSE, builds a one-entry S/G list to the sense buffer, disables disconnect/tagging for that command, optionally marks it for renegotiation, and requeues it.

The chunk ends with `ahd_loadseq()` computing downloadable constants for S/G prefetch behavior, including cacheline alignment, S/G element size, prefetch limits, packet-overrun buffer offset, and transfer size. It has just entered the loop over sequencer instructions and patch/critical-section metadata.

## State and Persistence Behavior

Most state is runtime controller state in `struct ahd_softc`, not persistent storage. The important live state includes mode caches, interrupt enable bits in `pause`/`unpause`, pending SCB lists, qin/qout ring offsets, command-completion buckets, target negotiation tables, message buffers and flags, target-mode event rings, queue freeze counts, and bug/workaround flags.

Transfer negotiation has three logical layers per target: `user`, `goal`, and `curr`. User settings come from defaults or EEPROM, goal settings track desired negotiated behavior, and current settings represent the active bus agreement. `ahd_update_neg_request()` persists the need for future negotiation in `tstate->auto_negotiate`; `ahd_update_neg_table()` persists current settings into the chip's negotiation RAM.

SCB state is split between host memory and adapter scratch/SCB RAM. HSCBs and S/G lists are DMA-coherent only after explicit `ahd_dmamap_sync()` calls. Completion paths may need to copy an HSCB back from SCB RAM before host-side status/residual handling. `ahd_swap_with_next_hscb()` deliberately changes HSCB ownership so the adapter can always fetch the physical HSCB address it already knows.

Resets intentionally discard or rebuild volatile hardware state. `ahd_reset()` preserves termination-related `SXFRCTL1`, handles PCI-X reset bugs, resets the chip, restores mode state, and optionally reinitializes the chip. `ahd_reset_channel()` aborts matching SCBs, clears FIFOs, clears message state, resets negotiation to async/narrow for all enabled target/initiator pairs, sends CAM async reset notifications, and restarts the sequencer.

EEPROM/VPD data is parsed but not written in this chunk. `ahd_parse_cfgdata()` and `ahd_parse_vpddata()` import persistent firmware configuration into runtime flags and user transfer settings. Actual SEEPROM read/write helpers appear after this chunk.

## Dependencies and Integration Points

- Hardware register access is abstracted through `ahd_inb()`, `ahd_outb()`, `ahd_outw_atomic()`, `ahd_insb()`, mode assertions, and PCI config helpers supplied by the OS/platform layer.
- DMA allocation, loading, unloading, and synchronization use `ahd_dma_tag_create()`, `ahd_dmamem_alloc()`, `ahd_dmamap_load()`, `ahd_dmamap_sync()`, and related wrappers from `aic79xx_osm.h`.
- SCSI/CAM integration uses platform callbacks such as `ahd_done()`, `ahd_send_async()`, `ahd_platform_freeze_devq()`, `ahd_platform_abort_scbs()`, `ahd_platform_set_tags()`, `ahd_print_path()`, and transaction status/tag/residual helpers.
- SPI message helpers `spi_populate_sync_msg()`, `spi_populate_width_msg()`, and `spi_populate_ppr_msg()` build SDTR/WDTR/PPR message bytes.
- The sequencer program and patch metadata come from `aic79xx_seq.h` and `aicasm/aicasm_insformat.h`.
- Linux kernel services used directly include allocation helpers, timers, jiffies, spinlock wrappers through `ahd_lock()`, `printk()`, `panic()`, list/queue macros, and conditional target-mode `xpt_*` CAM compatibility functions.
- Platform-specific attach/probe code outside this chunk supplies PCI identity, bug/feature masks, parent DMA tags, interrupt registration, and host registration.

## Risks and Edge Cases

- Register mode correctness is critical. Many helpers assume SCSI, CCHAN, DFF0, DFF1, or CFG mode on entry; a missing save/restore or wrong mode can corrupt unrelated register banks.
- The pause/unpause path is subtle. `ahd_unpause()` may restore saved modes and reset pending command counts, but only releases the sequencer if no non-command-complete interrupt remains.
- QOUTFIFO completion processing avoids PCI reads for speed. Races with posted writes, valid-tag toggles, and the `AHD_INTCOLLISION_BUG` workaround can lose or duplicate interrupt handling if changed casually.
- `ahd_flush_qoutfifo()` reimplements parts of firmware FIFO behavior in software. It must stay synchronized with sequencer algorithms for CFG4DATA, SAVEPTRS, S/G loading, residual tracking, and complete-list handling.
- Packetized recovery is highly state-dependent. LQI/LQO CRC, phase, busfree, and PPR/IU-change cases deliberately distinguish expected busfree from command loss; broad reset changes can regress U320 devices.
- Transfer negotiation updates must keep `user`, `goal`, `curr`, auto-negotiate bits, pending HSCB `MK_MESSAGE` bits, and chip negotiation table entries consistent.
- Message parsing indexes raw SCSI message buffers. Incomplete extended messages are intentionally handled incrementally; bounds or length changes can break multi-byte phase handling.
- `ahd_handle_msg_reject()` assumes `scb` is valid before checking tag rejection paths. It is reached during active message handling, but future callers should preserve that precondition.
- SCB collision-list logic protects non-packetized tagged contexts from hardware tag collisions. Free-list refactors can break fairness or allow reuse of a colliding tag while the other command is still active.
- Reset paths call abort/search routines that mutate QINFIFO, waiting-TID lists, pending lists, busy tables, and platform queues. Incorrect `CMDS_PENDING` or qfreeze accounting can stall the sequencer or over-release queues.
- Autosense reuses the failed SCB and replaces its command/S/G state. Residuals must be saved before rebuilding the SCB, and sense residuals must not clobber the original command residual.
- Hardware workarounds are chip-revision specific: PCI-X SCBRAM read, PCI-X CHIPRST parity, long selection timeout, packetized LUN, packetized status, delayed NLQI CRC, busfree revision, SCSI reset, CLRLQO autoclear, paced negotiation-table, IOCELL, LQO overrun, packet bitbucket, and slow CRC.
- `ahd_loadseq()` computes prefetch constants from PCI cacheline and S/G element size; invalid alignment assumptions can make the downloaded sequencer fetch partial or impossible S/G entries.
- Several catastrophic paths call `panic()` after dumping state. This is intentional for impossible hardware/queue inconsistencies, but it makes regression testing on real hardware high impact.

## Test Signals

Useful validation signals for this chunk include:

- Driver attach logs showing correct chip name, channel width, SCSI ID, SCB count, termination warnings, and optional slow-CRC/workaround messages.
- Successful load with interrupts enabled, `ahd_init()` completing, `ahd_restart()` running, and no "No SCB space found", "Failed chip reset", or sequencer download warnings.
- I/O completion under load with QOUTFIFO valid-tag wraparound, no "WARNING no command for scb", no QINFIFO/list loop panics, and stable command completion counters.
- SCSI negotiation logs under `bootverbose`: initial async/narrow state, SDTR/WDTR/PPR exchange, fallback when messages are rejected, and async/narrow reset after bus reset or target reset.
- Error-injection or hardware fault tests for selection timeout, unexpected busfree, parity/CRC, data overrun, packetized LQ failures, target reset, and bus reset, checking that commands complete with CAM status rather than hanging.
- Autosense coverage for CHECK CONDITION and packetized status IU, including sense-buffer DMA sync, residual preservation, `SCB_SENSE` cleanup, and CAM autosense failure reporting.
- Suspend/resume tests where `ahd_pause_and_flushwork()` drains pending work, suspend refuses active SCBs with `EBUSY`, and resume reinitializes the chip, enables interrupts, and restarts cleanly.
- Target-mode builds, if enabled, should validate immediate notify delivery for bus reset, target reset, abort task, abort task set, and clear task set events.
- Debug dump paths (`AHD_DEBUG`, tracepoints, `DUMP_CARD_STATE`) should produce coherent mode, SCB, FIFO, and negotiation state without causing secondary register-mode corruption.

### subset-b-005230: lines 9381-10724

# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_core.c lines 9381-10724

## Scope

This chunk covers the tail of the AIC79xx core driver. It begins in the final loop of `ahd_loadseq()`, where the compiled sequencer firmware is patched, address-fixed, parity-adjusted, and downloaded into controller sequencer RAM. It then defines sequencer patch/address helpers, diagnostic register dumping, SEEPROM and flexport accessors, checksum validators, and the end-of-file target-mode command intake path guarded by `AHD_TARGET_MODE`.

The chunk is not a standalone module. It depends on earlier definitions in `aic79xx_core.c`, generated sequencer arrays such as `seqprog`, `patches`, and `critical_sections`, register definitions from the shipped/generated AIC79xx register headers, and public structures/prototypes in `aic79xx.h`. The target-mode code is also partly compile-time-gated: the whole target-mode section requires `AHD_TARGET_MODE`, and the LUN enable/disable and SCSI-ID update bodies are additionally wrapped in `#if NOT_YET`, so those routines are present as scaffolding but not active in normal builds.

## Purpose

The visible code supports three late-stage responsibilities in the driver:

- Finish making the controller firmware image match the probed hardware and driver mode, then place it into sequencer RAM.
- Provide high-value diagnostics for SCSI error handling by dumping controller registers, SCB queues, FIFO state, DMA counters, LQ state, CDB bytes, and the sequencer stack while preserving execution state.
- Read, write, and validate persistent controller configuration data from the serial EEPROM and flexport-attached board logic.
- When target mode is compiled in, translate incoming target command DMA entries into CAM `ccb_accept_tio` completions and maintain the host/sequencer target command FIFO position.

This chunk therefore sits at the boundary between software policy and hardware state. It both mutates persistent adapter settings through SEEPROM/flexport writes and snapshots volatile card state for post-fault debugging.

## Important APIs, Types, and Functions

Sequencer firmware helpers:

- `ahd_check_patch(struct ahd_softc *ahd, const struct patch **start_patch, u_int start_instr, u_int *skip_addr)` walks the sorted `patches[]` table at the current source instruction. It calls each patch predicate, sets `skip_addr` when a patch is rejected, and advances the caller's patch cursor.
- `ahd_resolve_seqaddr(struct ahd_softc *ahd, u_int address)` recomputes a sequencer branch target after rejected patch blocks have been removed. It reruns patch decisions from instruction zero up to the original target and subtracts skipped instruction count.
- `ahd_download_instr(struct ahd_softc *ahd, u_int instrptr, uint8_t *dconsts)` decodes a 32-bit sequencer instruction from `seqprog`, resolves branch/call targets, replaces symbolic download constants when the instruction's parity bit is used as the marker, recalculates odd parity, endian-converts back to little endian, and writes four bytes to `SEQRAM`.
- The visible tail of `ahd_loadseq()` records downloaded critical section ranges in `ahd->critical_sections`, stores `ahd->num_critical_sections`, leaves `SEQCTL0` in normal `PERRORDIS|FAILDIS|FASTMODE` state, and emits verbose firmware feature/bug/flag data.

Diagnostics:

- `ahd_probe_stack_size()` destructively probes the sequencer `STACK` register depth by writing nonzero patterns and reading them back until the hardware no longer returns the expected LIFO sequence.
- `ahd_print_register()` is a generic bitfield printer used by generated register-specific print helpers. It prints the raw register value and decodes non-overlapping masks from an `ahd_reg_parse_entry_t` table.
- `ahd_dump_card_state()` is the central card dump routine. It pauses the card if needed, saves/restores register modes, iterates through mode-independent registers, pending/free SCB lists, sequencer completion lists, both DFF FIFO contexts, LQ state, current SCB/CDB fields, and the sequencer stack.
- `ahd_dump_scbs()` is present only under `#if 0`; it would dump every hardware SCB's control, SCSI ID, next pointers, and SG pointers, but is not compiled.

SEEPROM and flexport:

- `ahd_read_seeprom(struct ahd_softc *ahd, uint16_t *buf, u_int start_addr, u_int count, int bytestream)` reads 16-bit words through the controller SEEPROM state machine using `SEEADR`, `SEECTL`, and `SEEDAT`.
- `ahd_write_seeprom(struct ahd_softc *ahd, uint16_t *buf, u_int start_addr, u_int count)` enables SEEPROM writes, writes each word, then disables writes again.
- `ahd_wait_seeprom()` polls `SEESTAT` until `SEEARBACK|SEEBUSY` clears or a timeout expires.
- `ahd_verify_vpd_cksum(struct vpd_config *vpd)` validates the two 8-bit checksum regions in VPD data. It is static and used by earlier PCI/VPD parsing code in the same file.
- `ahd_verify_cksum(struct seeprom_config *sc)` validates the 16-bit SEEPROM checksum over all words except the checksum word.
- `ahd_acquire_seeprom()` currently always returns success; a flexport-based presence probe is compiled out because not every implementation exposes the logic.
- `ahd_release_seeprom()` is a no-op counterpart.
- `ahd_wait_flexport()`, `ahd_write_flexport()`, and `ahd_read_flexport()` arbitrate the flexport board-control interface through `BRDCTL`/`BRDDAT`, validate the 3-bit address range, and propagate timeout errors.

Target mode, when enabled:

- `ahd_find_tmode_devs()` maps a CAM CCB target/LUN to `struct ahd_tmode_tstate` and `struct ahd_tmode_lstate` pointers, validating target width and `AHD_NUM_LUNS`; wildcard target/LUN maps to the black-hole LUN.
- `ahd_handle_en_lun()` contains a full LUN enable/disable algorithm, but its body is disabled by `#if NOT_YET`. The inactive code allocates LUN state, creates CAM paths, toggles select-in through `SCSISEQ_TEMPLATE`/`SCSISEQ1`, updates target IDs, and reloads sequencer firmware when changing initiator/target roles.
- `ahd_update_scsiid()` is also disabled by `#if NOT_YET`; the inactive code would keep the active `SCSIID` OID consistent with the multi-target ID mask.
- `ahd_run_tqinfifo()` drains the DMA-backed target command FIFO, calls `ahd_handle_target_cmd()`, clears processed `cmd_valid` bytes, resyncs each consumed `struct target_cmd` for device preread, increments `ahd->tqinfifonext`, and lazily mirrors the host position into `HS_MAILBOX`.
- `ahd_handle_target_cmd()` converts a firmware-produced `struct target_cmd` into an ATIO CCB: it decodes initiator/target/LUN, finds or falls back to the black-hole LUN state, consumes an available accept-TIO CCB, copies tag metadata and CDB bytes, handles non-disconnect commands by freezing the CCB and recording `ahd->pending_device`, then completes the CCB via `xpt_done()`.

Key data structures in this chunk and adjacent headers include `struct ahd_softc`, `struct cs`, `struct patch`, `union ins_formats`, `struct scb`, `struct seeprom_config`, `struct vpd_config`, `struct target_cmd`, `struct ahd_tmode_tstate`, and `struct ahd_tmode_lstate`.

## Control Flow

The sequencer download path starts from earlier `ahd_loadseq()` setup that calculates download constants and enters `LOADRAM` mode. In the visible range, each source sequencer instruction is checked against patch predicates. Rejected patch spans are not downloaded. For accepted instructions, critical section source ranges are translated to downloaded instruction addresses, then `ahd_download_instr()` writes the rewritten instruction. After the loop, downloaded critical section ranges are copied into dynamically allocated driver state, the sequencer exits load mode, and verbose diagnostics report the resulting firmware size and active feature/bug/flag set.

Patch application and branch target rewriting are intentionally coupled. `ahd_check_patch()` is stateful for the primary download loop because it advances the caller's `cur_patch` cursor; `ahd_resolve_seqaddr()` uses a fresh cursor and replay of the same predicates to compute the address delta for each branch target. Any predicate with side effects would therefore be dangerous, because branch resolution assumes repeated evaluations produce identical decisions for the same `ahd_softc` state.

`ahd_download_instr()` handles opcodes by class. Branch and call opcodes first resolve their format-3 target, then fall through to format-1 immediate handling. Arithmetic/logical/block-move opcodes treat a nonzero parity bit as a marker that the immediate byte indexes `dconsts[]`; after substitution they clear parity and fall through to parity generation. `AIC_OP_ROL` does only parity generation and output. Unknown opcodes panic because a corrupt or mismatched sequencer image is unrecoverable.

`ahd_dump_card_state()` follows a preserve-and-restore pattern. It pauses only if the card is not already paused, saves current modes, switches through SCSI, DFF0, DFF1, CFG, CCHAN, and saved modes to read the relevant register banks, restores the sequencer stack contents after printing them, restores modes, and unpauses only if it paused the card itself. The dump also bounds pending/free/completion walks with `AHD_SCB_MAX` to avoid infinite output on corrupted lists.

SEEPROM reads and writes are linear register-machine operations. Reads initialize `error` to `EINVAL`, so a zero-length read returns invalid argument. Each iteration writes the word address, starts a read, waits, and copies either the machine-endian word from `ahd_inw(SEEDAT)` or two raw bytes when `bytestream` is set. Writes enable the chip first, initialize `retval` to `EINVAL` for zero-length writes, write each word/address/command tuple, break on per-word timeout, then always attempts write-disable; a write-disable failure overrides the per-word return.

Flexport access is a shorter arbitration flow. Both read and write assert SCSI mode, reject addresses above 7 via panic, request the encoded address through `BRDCTL`, wait for `FLXARBACK`, then either strobe `BRDDAT` for write or sample it for read. Both paths clear `BRDCTL` and flush posted writes to leave the board-control bus idle.

The active target-mode drain path starts when earlier interrupt or event handling calls `ahd_run_tqinfifo()`. It syncs the FIFO DMA area after device writes, processes entries until `cmd_valid` is clear or resources are unavailable, and publishes host progress periodically by updating the `HOST_TQINPOS` bits in `HS_MAILBOX`. Resource unavailability is signaled by `ahd_handle_target_cmd()` returning 1 when no `ccb_accept_tio` is queued for the selected LUN.

## State and Persistence

Persistent controller state affected by this chunk includes:

- SEEPROM contents written by `ahd_write_seeprom()`. These settings are adapter NVRAM and can survive driver unloads and reboots.
- Flexport board-control state written by `ahd_write_flexport()`, especially termination/current-sensing control used by earlier setup paths.
- Loaded sequencer firmware in controller `SEQRAM`, which persists for the lifetime of the controller instance until reset/reload.

Runtime state stored in `struct ahd_softc` includes:

- `ahd->num_critical_sections` and `ahd->critical_sections`, derived from the patched firmware image and later used when coordinating sequencer critical sections.
- `ahd->features`, `ahd->bugs`, and `ahd->flags`, consumed by patch predicates and printed after firmware download.
- Queue and SCB diagnostic state such as `pending_scbs`, free SCB lists, completion-list head registers, current `SCBPTR`, and saved `STACK` entries.
- Target-mode state, when enabled, in `enabled_targets[]`, `black_hole`, `pending_device`, `targetcmds`, `tqinfifonext`, and `AHD_TQINFIFO_BLOCKED`.

Most diagnostic reads are volatile snapshots. `ahd_dump_card_state()` temporarily changes card mode and SCB pointer and reads through FIFO/stack registers that have side effects; it deliberately restores the saved stack and mode but still runs in a fragile error context where concurrent hardware progress must be controlled by pausing.

## Dependencies and Integration Points

This chunk depends heavily on the driver register access layer: `ahd_inb/outb`, `ahd_inw/outw`, `ahd_inl`, `ahd_outsb`, `ahd_inb_scbram`, `ahd_inw_scbram`, `ahd_inl_scbram`, `ahd_set_modes()`, `ahd_save_modes()`, `ahd_restore_modes()`, `ahd_pause()`, `ahd_unpause()`, `ahd_flush_device_writes()`, `ahd_delay()`, and DMA sync wrappers.

It integrates with earlier and adjacent driver code through these call sites:

- `ahd_loadseq()` is invoked during initialization/reinitialization and in the inactive target-mode role-switch path.
- `ahd_dump_card_state()` is called from many error and recovery paths in `aic79xx_core.c`, from PCI setup error handling, and from OS-specific paths in `aic79xx_osm.c`.
- `ahd_read_seeprom()`, `ahd_write_seeprom()`, and `ahd_verify_cksum()` are used by PCI probing/config parsing and by procfs SEEPROM update paths.
- `ahd_read_flexport()` and `ahd_write_flexport()` are used by termination/current-sensing setup in this file and by PCI board setup.
- `ahd_run_tqinfifo()` is called by interrupt/event handling when target-mode incoming commands are pending.

The target-mode code integrates with CAM concepts (`union ccb`, `ccb_accept_tio`, `CAM_*` status values, `xpt_done()`, `xpt_create_path()`, `xpt_free_path()`, `xpt_path_comp()`) and SCSI message/CDB decoding macros. In this Linux-imported tree, much of that target-mode support appears to be compatibility code shared with the original FreeBSD-derived driver and is not necessarily enabled in ordinary Linux builds.

## Risks and Edge Cases

- Patch predicates must be deterministic. `ahd_resolve_seqaddr()` replays patch decisions independently of the main download loop; any predicate that observes mutable hardware state or changes state could produce incorrect branch targets.
- `ahd_download_instr()` casts `&seqprog[instrptr * 4]` to `uint32_t *`. This assumes the sequencer byte array is suitably accessible for unaligned little-endian loads on the target architecture or that compiler/platform constraints make it safe.
- Download constant substitution uses the instruction parity bit as an out-of-band marker. A bad immediate index can read beyond `dconsts[]`, and a malformed firmware image can panic on an unknown opcode.
- `ahd_loadseq()` allocates critical section data with `GFP_ATOMIC` and panics on failure. That matches low-level driver expectations but makes memory pressure during initialization/reload fatal.
- `ahd_print_register()` updates `*cur_column` in the `table == NULL` path without checking `cur_column`; current callers appear to pass a pointer, but the public signature allows `NULL`.
- `ahd_dump_card_state()` is intentionally invasive. It pauses the device, walks potentially corrupt lists, changes mode banks, changes `SCBPTR`, pops and pushes stack entries, and may produce large kernel logs. Its bounded loops reduce but do not eliminate diagnostic-side risk.
- SEEPROM write paths can partially modify persistent NVRAM before returning an error. The function disables writes afterward, but callers must treat nonzero returns as possible partial writes and revalidate checksums.
- Zero-length SEEPROM read/write returns `EINVAL` by design. Callers must not interpret that as successful no-op behavior.
- `ahd_acquire_seeprom()` unconditionally returning success means boards without SEEPROM support are detected later by read/checksum failure rather than acquisition failure.
- Flexport address errors panic rather than returning `EINVAL`, so callers must validate any non-constant addresses before calling.
- `ahd_handle_target_cmd()` assumes a valid `lstate` after falling back to `ahd->black_hole`; if target mode were enabled without a black-hole LUN for disabled targets, dereferencing `lstate->accept_tios` would fault.
- Target command parsing trusts the firmware-provided `bytes[]` layout. It advances over optional tag bytes and one terminator byte, then copies a CDB length based on the opcode group; malformed entries could make the copied CDB semantically invalid even though the fixed 22-byte buffer bounds limit the normal CDB sizes used here.

## Test and Validation Signals

Useful validation for this chunk is mostly hardware, fault-injection, and driver-integration oriented:

- Boot or probe with representative AIC79xx hardware should show successful sequencer download, expected instruction count under `bootverbose`, and no unknown-opcode or critical-section allocation panics.
- Firmware patch matrix testing should cover feature/bug/flag combinations that accept and reject patch blocks, then verify sequencer branch/call targets land on the correct downloaded addresses.
- Fault injection around `kmemdup(..., GFP_ATOMIC)` would confirm the current panic behavior for critical-section allocation failure.
- Error-path tests that trigger `ahd_dump_card_state()` should confirm the card is unpaused only when the dump paused it, modes are restored, stack entries are restored, and SCB/completion list walks terminate on corrupted links.
- SEEPROM tests should cover zero-length operations, normal word reads, bytestream reads, timeout from `ahd_wait_seeprom()`, write-enable failure, per-word write timeout, write-disable timeout, checksum validation success/failure, and partial-write recovery by re-reading and validating the checksum.
- Flexport tests should cover read/write success, arbitration timeout, and all valid addresses 0-7; invalid addresses intentionally panic and should be tested only in controlled fault-injection environments.
- PCI/config integration should verify that VPD and SEEPROM checksum failures cause fallback/default configuration paths rather than accepting corrupt adapter settings.
- If `AHD_TARGET_MODE` is enabled, target-mode tests should queue ATIO CCBs, inject target command FIFO entries with and without tag bytes, verify CDB length decoding for command groups 0/1/2/4/5 and reserved groups, exercise black-hole LUN handling, confirm `AHD_TQINFIFO_BLOCKED` toggles when ATIO resources run out, and check `HS_MAILBOX` host-position updates at the expected FIFO boundaries.
