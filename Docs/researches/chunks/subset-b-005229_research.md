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
