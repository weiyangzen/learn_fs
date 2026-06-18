# Research: subset-b-005237

This grouped report covers the ARM SCSI driver files in `sources/distributed-fs/ceph-client/drivers/scsi/arm/`. Each section is source-path aligned for reconciliation into the corresponding per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.c

## Purpose

`acornscsi.c` implements the Acorn SCSI 3 host adapter driver for Acorn expansion cards using a WD33C93A SBIC plus an on-board uPC71071-style DMAC and paged DMA RAM. Unlike the FAS216-based card wrappers in the same folder, this file owns its own SCSI command queueing, phase state machine, reconnect/disconnect handling, message handling, DMA-buffer management, abort/reset handling, proc display, expansion-card probe/remove, and Linux SCSI host-template callbacks.

## Important APIs, Types, and Functions

The Linux-facing entry points are `acornscsi_queuecmd`, `acornscsi_abort`, `acornscsi_host_reset`, `acornscsi_show_info`, `acornscsi_info`, `acornscsi_probe`, `acornscsi_remove`, `acornscsi_init`, and `acornscsi_exit`. The host-private state is `AS_Host` from `acornscsi.h`; per-command state uses `struct arm_cmd_priv` and `arm_scsi_pointer()` from `arm_scsi.h`.

Important internal surfaces include SBIC access helpers (`sbic_arm_read`, `sbic_arm_write`, `acornscsi_sbic_issuecmd`, `acornscsi_sbic_wait`, `acornscsi_sbic_xfcount`), card reset (`acornscsi_resetcard`), command scheduling (`acornscsi_kick`, `acornscsi_done`), DMA handling (`acornscsi_dma_setup`, `acornscsi_dma_stop`, `acornscsi_dma_cleanup`, `acornscsi_dma_intr`, `acornscsi_dma_xfer`, `acornscsi_dma_adjust`), data movement (`acornscsi_data_read`, `acornscsi_data_write`, `acornscsi_starttransfer`), message handling (`acornscsi_buildmessages`, `acornscsi_sendmessage`, `acornscsi_message`, `acornscsi_abortcmd`), reconnect handling (`acornscsi_reconnect`, `acornscsi_reconnect_finish`), and the main interrupt state machine (`acornscsi_intr`, `acornscsi_sbicintr`).

## Control Flow

Probe claims expansion-card resources, allocates a `Scsi_Host`, maps MEMC and IOCFAST windows, registers the IRQ, initializes issue/disconnected queues plus the message queue, resets the card, calls `scsi_add_host()`, and scans. Queueing initializes the command's saved SCSI pointer, classifies data direction, pushes the command into the ordered issue queue, and kicks the adapter when idle.

The interrupt path loops until no more work is pending. It handles DMAC terminal-count work first, dispatches SBIC interrupts through `acornscsi_sbicintr()`, performs delayed DMA RAM copies when required, and starts the next command when a command reaches `INTR_NEXT_COMMAND`. `acornscsi_sbicintr()` is a large phase table keyed by WD33C93A SSR values and driver phases such as connecting, connected, message out, command, data in/out, status in, message in, done, aborted, disconnected, and reconnected.

Data transfers are staged through the card's on-board DMA memory. For input, the DMAC fills card memory and the driver later copies it to the scatterlist buffer; for output, the driver preloads card memory from the scatterlist and corrects the DMAC address when the SBIC/SCSI bus lags the DMAC.

## State and Persistence Behavior

There is no durable persistence. Runtime state lives in `AS_Host`: current and original commands, issue/disconnected queues, per-target sync/disconnect capabilities, busy LUN bits, message queue, command statistics, SBIC status history, card page-register state, and DMA ring-buffer state (`free_addr`, `start_addr`, transfer counters, scheduled copy metadata, and flags). Synchronous transfer state is per target and reset to negotiation state on card reset. Module globals `sdtr_period` and `sdtr_size` configure synchronous transfer request values.

## Dependencies and Integration Points

The driver depends on ARM expansion-card APIs (`ecard_request_resources`, `ecardm_iomap`, `ecard_set_drvdata`, `ecard_register_driver`), Linux SCSI mid-layer APIs, SCSI transport SPI definitions for messages, the shared queue and message-queue modules, and `arm_scsi.h` scatterlist pointer helpers. It also references external assembly helpers `__acornscsi_in` and `__acornscsi_out` for card-memory copies.

## Risks and Edge Cases

The state machine is highly hardware-specific and uses raw numeric SSR values. Lost, repeated, or unexpected phase transitions can abort commands or leave busy LUN bits set. `DEBUG_NO_WRITE` and `NO_WRITE 0xFE` actively reject writes to all targets except target 0 in this source configuration, which is a major behavior signal. DMA write correction can report negative offsets if SBIC/DMAC accounting diverges. `acornscsi_host_reset()` removes disconnected commands without completing them in the visible loop, so reset/error handling needs careful validation. The file uses local IRQ save/restore rather than a single host lock in several paths, increasing race sensitivity around queue, disconnect, and abort handling.

## Test Signals

Useful signals include probe logs for IRQ/resource mapping, SCSI scan results, `/proc/scsi/acornscsi/*` statistics and phase history, successful READ paths across scatterlist boundaries, explicit WRITE rejection for `NO_WRITE` targets, disconnect/reconnect with and without tags, SDTR negotiation or rejection, abort of issue/disconnected/executing commands, host reset under active and disconnected commands, DMAC terminal-count handling, and incomplete-transfer warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.h

## Purpose

`acornscsi.h` is the private hardware and state header for `acornscsi.c`. It defines the WD33C93A SBIC register map, uPC71071 DMAC register map, bit definitions, driver phase enums, DMA/message/command enums, status-ring debugging structures, and the `AS_Host` per-adapter state layout.

## Important APIs, Types, and Functions

The central type is `AS_Host`, which stores host pointers, MMIO bases, current command pointers, SCSI phase state, reconnect identity, active `struct scsi_pointer`, message queue, statistics, issue/disconnected queues, per-target sync/disconnect information, busy LUN bitmap, DMA bookkeeping, card page-register state, and per-target/host status rings.

Important definitions include SBIC register constants (`SBIC_OWNID`, `SBIC_CTRL`, `SBIC_TRANSCNT*`, `SBIC_SYNCHTRANSFER`, `SBIC_CMND`, `SBIC_ASR`, `SBIC_SSR`), SBIC commands (`CMND_RESET`, `CMND_SELWITHATN`, `CMND_XFERINFO`, `CMND_ASSERTATN`, `CMND_NEGATEACK`), DMAC registers and masks, phase enums (`PHASE_*`), interrupt-return enums (`INTR_*`), DMA direction (`DMA_IN`, `DMA_OUT`), sync negotiation state (`SYNC_*`), command classes (`CMD_READ`, `CMD_WRITE`, `CMD_MISC`), and data direction values.

## Control Flow

The header encodes the vocabulary used by the implementation's state machine. SBIC command/status constants drive phase transitions, DMAC fields drive setup/cleanup, and `ADD_STATUS()` records a circular trace for each target plus host slot 8. `AS_Host` joins these hardware details to SCSI mid-layer state and shared queue/message modules.

## State and Persistence Behavior

The header defines only in-memory state. The persistent runtime state is per host and includes active/disconnected commands, queue state, target sync settings, busy LUN bits, DMA buffer pointers, and recent status traces. Reset paths reinitialize this state rather than reading or writing durable configuration.

## Dependencies and Integration Points

It includes `queue.h` and `msgqueue.h` and expects Linux SCSI structures to be visible from including code. The `struct scsi_pointer` embedded in `AS_Host` is populated through `arm_scsi.h` helpers. The constants are consumed directly by `acornscsi.c`.

## Risks and Edge Cases

This header is an ABI-like contract between the driver and specific Acorn SCSI hardware. Wrong bit definitions or enum assumptions can break command selection, message phases, DMA masking, or reset handling. `ADD_STATUS()` assumes `host` is in scope and uses power-of-two ring sizing. The busy-LUN bitmap is sized for 8 targets times 8 LUNs and assumes target/lun values fit that layout.

## Test Signals

Build coverage should catch missing SCSI/queue/message definitions. Runtime validation should inspect status rings, per-target sync values, busy-LUN clearing after disconnect/abort/reset, and correct SBIC/DMAC register programming during probe and transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/acornscsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/arm_scsi.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/arm_scsi.h

## Purpose

`arm_scsi.h` provides shared command-private scatterlist pointer helpers for the ARM SCSI drivers. It adapts modern `struct scsi_cmnd` scatter-gather state into the older `struct scsi_pointer` style used by the Acorn and FAS216 state machines.

## Important APIs, Types, and Functions

`struct arm_cmd_priv` wraps a `struct scsi_pointer` for SCSI command private storage. `arm_scsi_pointer(cmd)` returns the per-command pointer. `init_SCp()` initializes that pointer from `scsi_sglist()`, `scsi_sg_count()`, and `scsi_bufflen()`. `next_SCp()` advances to the next scatterlist entry. `get_next_SCp_byte()` and `put_next_SCp_byte()` transfer one byte through the current pointer. `copy_SCp_to_sg()` copies the current pointer plus remaining chained SG entries into a caller-provided contiguous SG array for ISA-style DMA setup.

## Control Flow

Callers invoke `init_SCp()` when queueing a command. Transfer engines consume or update the returned pointer as data is moved. DMA-capable card wrappers use `copy_SCp_to_sg()` to hand an aligned SG array to platform DMA APIs. `BELT_AND_BRACES` validation recomputes total SG length and clamps `phase` if `scsi_bufflen()` disagrees with actual SG lengths.

## State and Persistence Behavior

All state is command-private and in-memory. The active fields are the current SG entry, current virtual pointer, residual length in this segment, number of remaining segments, and total transfer phase count. No data is persisted outside the command lifetime.

## Dependencies and Integration Points

This header depends on Linux scatterlist and SCSI command APIs. It is used by `acornscsi.c`, `fas216.h`/`fas216.c`, and FAS216 card wrappers that need to map command buffers to legacy DMA controllers.

## Risks and Edge Cases

`copy_SCp_to_sg()` has a `BUG_ON(bufs + 1 > max)`, so callers must size fixed SG arrays correctly. The helpers use `sg_virt()` and direct byte dereferences, so they assume CPU-accessible SG memory. The length mismatch fallback is intentionally naive and logs a warning rather than failing the command. `get_next_SCp_byte()` and `put_next_SCp_byte()` do not advance to the next SG entry on their own.

## Test Signals

Tests should cover zero-length commands, single and multiple SG entries, SG count at the fixed array limit, mismatched `scsi_bufflen()` versus SG total length, and bytewise PIO crossing segment boundaries via caller-managed `next_SCp()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/arm_scsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/arxescsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/arxescsi.c

## Purpose

`arxescsi.c` is the ARXE 16-bit SCSI expansion-card driver. It is a board-specific wrapper around the generic FAS216 core and supplies card resource mapping, FAS216 timing/configuration, pseudo-DMA data movement, host-template callbacks, and expansion-card registration.

## Important APIs, Types, and Functions

`struct arxescsi_info` overlays `FAS216_Info` with the expansion card and base MMIO pointer. The card-specific DMA hooks are `arxescsi_dma_setup()`, `arxescsi_dma_pseudo()`, `arxescsi_pseudo_dma_write()`, and `arxescsi_dma_stop()`. User-visible reporting uses `arxescsi_info()` and `arxescsi_show_info()`. Lifecycle is `arxescsi_probe()`, `arxescsi_remove()`, `init_arxe_scsi_driver()`, and `exit_arxe_scsi_driver()`.

## Control Flow

Probe claims the expansion card, maps MEMC space, allocates a SCSI host, fills FAS216 register base, clock, select timeout, async period, sync depth, disconnect, and pseudo-DMA callbacks, configures expansion-card IRQ status fields, initializes the FAS216 core, and calls `fas216_add()`. Runtime command flow is delegated to `fas216_noqueue_command`, meaning the FAS216 core polls progress rather than using a registered IRQ for this board.

Pseudo DMA always advertises `fasdma_pseudo`. Reads and writes poll FAS216/card status, move 16-bit words through `DMADATA_OFFSET`, and stop early when the FAS216 interrupt bit is observed.

## State and Persistence Behavior

State is per host in `struct arxescsi_info` plus the embedded `FAS216_Info`. No settings persist. The pseudo-DMA code uses the current `struct scsi_pointer` buffer and does not retain additional transfer state outside FAS216's active command state.

## Dependencies and Integration Points

The file depends on ARM expansion-card APIs, MMIO helpers, Linux SCSI host APIs, and `fas216.h`. It integrates with the generic FAS216 state machine through DMA callbacks and the `scsi_host_template`.

## Risks and Edge Cases

The header comment says the driver is based on experimentation, so hardware assumptions are explicitly fragile. The inline ARM assembly write path is architecture-specific and assumes 256-byte chunks and particular register behavior. The read path has a conditional bulk-read branch tied to `transfer & 255`, which should be tested for short and unaligned transfers. Since no IRQ is used, progress relies on polling in `fas216_noqueue_command`.

## Test Signals

Signals include successful probe of `MANU_ARXE/PROD_ARXE_SCSI`, FAS216 chip detection, scan completion without IRQ, read/write pseudo-DMA with short, 256-byte, and multi-block transfers, disconnect disabled behavior, and clean removal/reprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/arxescsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_1.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_1.c

## Purpose

`cumana_1.c` implements the Cumana 16-bit SCSI-1 expansion-card driver using the generic NCR5380 core. It defines board-specific register access, pseudo-DMA read/write routines, IRQ setup, host-template glue, probe/remove, and module registration.

## Important APIs, Types, and Functions

The file specializes NCR5380 through macros such as `NCR5380_read`, `NCR5380_write`, `NCR5380_dma_xfer_len`, `NCR5380_dma_recv_setup`, `NCR5380_dma_send_setup`, `NCR5380_intr`, `NCR5380_queue_command`, and `NCR5380_info`. Card-specific helpers are `cumanascsi_read()`, `cumanascsi_write()`, `cumanascsi_pread()`, `cumanascsi_pwrite()`, `cumanascsi_dma_xfer_len()`, `cumanascsi1_probe()`, and `cumanascsi1_remove()`.

## Control Flow

Probe claims resources, allocates an NCR5380-sized host, maps slow IOC space for control/registers and MEMC space for pseudo-DMA, initializes the NCR5380 core with DMA fixup and late DMA setup flags, maybe resets the bus, enables card control, requests the IRQ, adds the host, and scans. The included `../NCR5380.c` supplies queueing, interrupt, and error handling under the Cumana-specific macros.

PIO-style pseudo DMA switches card control modes, polls status bits for interrupt or ready, transfers fast 32-byte chunks as split 16-bit writes/reads, handles trailing bytes, and restores the control latch.

## State and Persistence Behavior

State is NCR5380 hostdata plus an added `ctrl` implementation field storing the current control latch. No durable state is written. Runtime state is managed mostly inside the included NCR5380 core and SCSI mid-layer.

## Dependencies and Integration Points

The file depends on ARM ecard APIs, MMIO helpers, Linux SCSI host APIs, and the generic NCR5380 implementation. It integrates with SCSI through `cumanascsi_template`, IRQ registration, `scsi_add_host()`, and `scsi_scan_host()`.

## Risks and Edge Cases

The source includes `../NCR5380.c` directly, so macro definitions must be correct before inclusion. Pseudo-DMA casts buffers to `unsigned long *` and performs word chunking, making alignment and trailing byte handling important. `cumanascsi_dma_xfer_len()` returns `cmd->transfersize`, not total residual length, so behavior depends on mid-layer transfer-size semantics. Cleanup must unmap both IO windows on partial probe failure.

## Test Signals

Useful checks include probe/remove with both MMIO windows, IRQ delivery, NCR5380 bus reset and scan, pseudo-DMA read/write for 0-byte, sub-32-byte, 32-byte, and larger transfers, interrupt-aborted transfer handling, and `/proc` host naming as `CumanaSCSI-1`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_2.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_2.c

## Purpose

`cumana_2.c` is the Cumana SCSI II expansion-card driver. It wraps the generic FAS216 core, provides real DMA and pseudo-DMA support, controls bus termination, exposes proc write/show hooks, and registers the expansion-card driver.

## Important APIs, Types, and Functions

`struct cumanascsi2_info` embeds `FAS216_Info`, card/base pointers, terminator state, and a fixed SG array. Board hooks are `cumanascsi_2_irqenable()`, `cumanascsi_2_irqdisable()`, `cumanascsi_2_terminator_ctl()`, `cumanascsi_2_intr()`, `cumanascsi_2_dma_setup()`, `cumanascsi_2_dma_pseudo()`, and `cumanascsi_2_dma_stop()`. Reporting/configuration uses `cumanascsi_2_info()`, `cumanascsi_2_set_proc_info()`, and `cumanascsi_2_show_info()`. Lifecycle is `cumanascsi2_probe()` and `cumanascsi2_remove()`.

## Control Flow

Probe maps MEMC space, allocates a host, stores drvdata, applies slot-based module parameter `term[]`, configures FAS216 timing and callbacks, installs expansion-card IRQ ops, initializes FAS216, requests IRQ and optional DMA channel, enables DMA capability when available, then calls `fas216_add()`. Runtime command processing is `fas216_queue_command`; interrupts call `fas216_intr()`.

DMA setup disables card DMA, then either maps the current SCSI pointer into the fixed SG array and programs the platform DMA channel for sufficiently large or required transfers, or falls back to pseudo/PIO. Pseudo-DMA implements reads from the board FIFO; the write pseudo-DMA branch is disabled and prints `PSEUDO_OUT???`.

## State and Persistence Behavior

Persistent runtime state is per host: terminator flag, fixed SG list, embedded FAS216 queues/device state, and optional DMA channel ownership. The `term[]` module parameter supplies initial per-slot termination but is not persisted.

## Dependencies and Integration Points

The file depends on FAS216 core APIs, `arm_scsi.h` for `copy_SCp_to_sg()`, ARM DMA APIs, ecard IRQ hooks, Linux SCSI host APIs, and optional proc write support via the host template.

## Risks and Edge Cases

`dma_map_sg()` return value is ignored and the driver does not visibly unmap SG mappings in `dma_stop()`, which should be checked against platform DMA expectations. The pseudo-DMA data-out path is effectively unimplemented, so fallback writes can fail or only log. `copy_SCp_to_sg()` can BUG if SG count exceeds `NR_SG`. Termination can be modified via proc-style input with minimal parsing.

## Test Signals

Validate slot-based termination, proc `term=0/1`, IRQ enable/disable, real DMA read/write above 512 bytes, fallback PIO/pseudo reads below threshold, behavior when DMA request fails, FAS216 disconnect/sync negotiation, and clean resource release for IRQ and DMA on probe failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/cumana_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/eesox.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/eesox.c

## Purpose

`eesox.c` implements the EESOX Fast SCSI expansion-card driver. It is a FAS216 wrapper with card-specific control latch management, optional real DMA, pseudo-DMA FIFO helpers, sysfs/proc termination control, IRQ wiring, and expansion-card lifecycle.

## Important APIs, Types, and Functions

`struct eesoxscsi_info` embeds `FAS216_Info`, card/base/control pointers, a control latch, and a fixed SG array. Key functions are `eesoxscsi_irqenable()`, `eesoxscsi_irqdisable()`, `eesoxscsi_terminator_ctl()`, `eesoxscsi_intr()`, `eesoxscsi_dma_setup()`, `eesoxscsi_buffer_in()`, `eesoxscsi_buffer_out()`, `eesoxscsi_dma_pseudo()`, `eesoxscsi_dma_stop()`, `eesoxscsi_set_proc_info()`, sysfs `bus_term` show/store handlers, `eesoxscsi_probe()`, and `eesoxscsi_remove()`.

## Control Flow

Probe maps IOCFAST space, allocates a host, initializes the control latch from the `term[]` module parameter, sets FAS216 base/shift/timing/DMA callbacks, configures expansion-card IRQ status, creates a `bus_term` sysfs file, initializes FAS216, requests IRQ and optional DMA, then calls `fas216_add()`. Runtime commands and error handling are provided by FAS216.

Real DMA maps the current command SG list and programs the platform DMA channel when the transfer is required or at least 512 bytes. Otherwise the FAS216 core uses pseudo-DMA callbacks. Pseudo-DMA polls FAS216 status and board DMA status, uses FIFO count to decide transfer sizes, and performs aligned 16/32-bit FIFO accesses for input and output.

## State and Persistence Behavior

Runtime state consists of the control latch, termination bit, fixed SG array, optional DMA ownership, and embedded FAS216 command/device state. `term[]` only controls initial state. Sysfs/proc writes update the live control latch but do not persist across reload.

## Dependencies and Integration Points

The driver depends on ecard APIs, FAS216 APIs, `arm_scsi.h`, ARM DMA APIs, Linux device attributes, and Linux SCSI host callbacks. It exposes termination through both proc host write and `bus_term` sysfs attribute.

## Risks and Edge Cases

Control-latch updates are protected by `host_lock` for termination paths, but IRQ enable/disable also mutate the latch through ecard callbacks; concurrency should be checked. As in similar wrappers, `dma_map_sg()` return value and unmap behavior are risk points. Pseudo-DMA uses `(u32)buf` alignment tests, which are architecture-sensitive. `device_create_file()` return is ignored during probe.

## Test Signals

Check probe with and without DMA channel, sysfs and proc termination changes, IRQ enable/disable preserving termination bits, pseudo-DMA input/output for unaligned buffers and odd lengths, FAS216 scan/sync/disconnect behavior, and cleanup of sysfs, IRQ, DMA, and host resources on failure and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/eesox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/fas216.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/fas216.c

## Purpose

`fas216.c` is the generic SCSI protocol engine for FAS216/NCR53C9x/Am53CF94-style chips used by several ARM expansion-card drivers. Board files provide register base, timing, IRQ, DMA callbacks, and host template data; this file implements chip initialization, command queueing, message negotiation, interrupt-driven SCSI phase handling, DMA/PIO transfer coordination, disconnect/reconnect queues, automatic request sense, error handling, reset handling, diagnostics, and exported helper APIs.

## Important APIs, Types, and Functions

Exports include `fas216_init`, `fas216_add`, `fas216_queue_command`, `fas216_noqueue_command`, `fas216_intr`, `fas216_remove`, `fas216_release`, `fas216_eh_abort`, `fas216_eh_device_reset`, `fas216_eh_bus_reset`, `fas216_eh_host_reset`, `fas216_print_host`, `fas216_print_stats`, and `fas216_print_devices`.

Important internals include register helpers (`fas216_readb`, `fas216_writeb`, `fas216_cmd`), sync negotiation (`fas216_syncperiod`, `fas216_set_sync`, `fas216_handlesync`), transfer handling (`fas216_transfer`, `fas216_stoptransfer`, `fas216_aborttransfer`, `fas216_cleanuptransfer`, `fas216_updateptrs`, `fas216_pio`), message handling (`fas216_message`, `fas216_parse_message`, `fas216_send_messageout`), command launch (`fas216_start_command`, `__fas216_start_command`, `fas216_kick`), completion (`fas216_done`, `fas216_std_done`, `fas216_rq_sns_done`), interrupt subhandlers (`fas216_disconnect_intr`, `fas216_reselected_intr`, `fas216_busservice_intr`, `fas216_funcdone_intr`), reset logic (`fas216_bus_reset`, `fas216_init_chip`, `fas216_reset_state`, `fas216_detect_type`), and command lookup for EH (`fas216_find_command`).

## Control Flow

`fas216_init()` initializes shared state, queues, message queue, waitqueue, timer, magic guards, config register defaults, and async transfer timing. `fas216_add()` validates clock rate, resets state, detects chip type, initializes registers, issues a SCSI bus reset, then adds and scans the host. Board IRQ handlers call `fas216_intr()`, which reads `REG_STAT`, `REG_IS`, and `REG_INST` and dispatches bus reset, illegal command, disconnect, reselect, bus service, and function-done events.

Queueing stores the completion callback, initializes the command's SCSI pointer, puts the command on the issue queue, and kicks the interface if idle. `fas216_kick()` prioritizes device reset commands, automatic request-sense commands, original commands, then issue-queue commands not blocked by `busyluns`. Selection sends IDENTIFY, optional tag, and SDTR messages. Interrupts drive legal SCSI phase transitions between message, command, data, status, disconnect, reconnect, and done states. CHECK CONDITION or COMMAND TERMINATED triggers `scsi_eh_prep_cmnd()` and a high-priority request-sense command before completing the original command.

## State and Persistence Behavior

No durable state is written. `FAS216_Info` stores all runtime state: current/original/request-sense/reset commands, issue/disconnected queues, busy LUN bitmap, per-target disconnect/parity/sync/wide negotiation fields, current active SCSI pointer, message queue, stats, DMA callback state, EH wait/timer fields, and chip configuration. Reset paths clear queues and per-target negotiation state. `level_mask` is a module parameter controlling logging.

## Dependencies and Integration Points

The file depends on `fas216.h`, `arm_scsi.h`, `queue.h`, `msgqueue.h`, Linux SCSI mid-layer/EH APIs, SCSI message constants, MMIO helpers, timers, waitqueues, and board-provided DMA callbacks. It is consumed by `arxescsi.c`, `cumana_2.c`, `eesox.c`, and `powertec.c`.

## Risks and Edge Cases

The SCSI phase table is complex and hardware-sensitive. Unexpected bus-service states often log and continue or complete with `DID_ERROR`. `fas216_bus_reset()` contains a visible `info->SCpnt = NULL; /* bug! */` comment, signaling known fragility around reset and in-flight command ownership. `fas216_add()` and `fas216_eh_host_reset()` temporarily unlock `host_lock` while sleeping, so callers must satisfy lock assumptions. DMA callbacks may be NULL or board-specific; incorrect transfer type decisions can cause missing stop callbacks or stale residuals. Reconnect handling assumes target/lun/tag matching and sends ABORT when no command is found. Automatic request sense reuses the original command and host_scribble callback path, so lifetime bugs can affect completion.

## Test Signals

Test FAS216 chip detection for NCR53C90, NCR53C90A, NCR53C9x, Am53CF94, Emulex FAS216, and QLogic FAS216 where possible; queueing with simple tags; SDTR negotiation, rejection, and async fallback; PIO, pseudo-DMA, block DMA, and whole-request DMA; disconnect/reconnect and save/restore pointers; CHECK CONDITION automatic request sense; abort of queued/disconnected/executing commands; device, bus, and host resets; bus reset interrupt reporting; and proc diagnostic output for stats/devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/fas216.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/fas216.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/fas216.h

## Purpose

`fas216.h` is the shared hardware and state contract for the generic FAS216/NCR53C9x driver core and board-specific wrappers. It defines chip registers and bits, SCSI phase enums, DMA mode enums, negotiation state, capability flags, `FAS216_Info`, per-command private data, inline accessors, and exported function prototypes.

## Important APIs, Types, and Functions

Important constants cover FAS registers (`REG_CTCL`, `REG_FF`, `REG_CMD`, `REG_STAT`, `REG_INST`, `REG_IS`, `REG_CNTL*`, `REG_ID`), commands (`CMD_TRANSFERINFO`, `CMD_SELECTATN`, `CMD_ENABLESEL`, `CMD_WITHDMA`), status/phase bits (`STAT_*`, `INST_*`, `IS_*`, `CFIS_CF`), config bits (`CNTL1_*`, `CNTL2_*`, `CNTL3_*`), and capabilities (`FASCAP_DMA`, `FASCAP_PSEUDODMA`).

Core types are `phase_t`, `fasdmadir_t`, `fasdmatype_t`, `neg_t`, `FAS216_Info`, `struct fas216_device`, and `struct fas216_cmd_priv`. Public APIs are declared for initialization, add/remove/release, queued and noqueue command entry points, IRQ handling, SCSI EH handlers, and proc-style printers.

## Control Flow

Board drivers allocate `struct Scsi_Host` with private data beginning with or containing `FAS216_Info`, fill the `scsi` hardware location and `ifcfg` timing/capability fields, install DMA callbacks, call `fas216_init()`, and then `fas216_add()`. The core uses fields in this header to drive queues, current command state, transfer state, per-target negotiation, and error recovery.

## State and Persistence Behavior

All state is in memory. `FAS216_Info` persists for the lifetime of the host and tracks current command ownership, reset state, queues, active SCSI pointer, messages, per-target sync/parity/disconnect settings, busy LUNs, DMA callback state, statistics, and EH wait/timer state. No durable settings are defined.

## Dependencies and Integration Points

The header includes SCSI EH definitions plus local `queue.h` and `msgqueue.h`. It expects Linux SCSI command/private data support and is included by the generic core and multiple card wrappers.

## Risks and Edge Cases

`struct fas216_cmd_priv` requires `scsi_pointer` as the first member to match `arm_scsi_pointer()`. Board wrappers must ensure their host-private layout is compatible with casts to `FAS216_Info`. DMA callback semantics are a cross-file contract: setup returns a `fasdmatype_t`, pseudo handles pseudo transfers, and stop is called only for real DMA types. Busy-LUN bitmap size and target assumptions are fixed at 8 targets and 8 LUNs.

## Test Signals

Build tests should catch command-private size mismatches and missing callbacks. Runtime signals include correct host-private casting, register programming from `ifcfg`, queue initialization/free, DMA callback invocation for each transfer type, per-target sync fields in diagnostics, and all exported EH handlers being callable from board templates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/fas216.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.c

## Purpose

`msgqueue.c` implements a tiny fixed-capacity SCSI message queue used by the Acorn and FAS216 drivers to build outgoing message sequences such as IDENTIFY, SIMPLE QUEUE TAG, SDTR, MESSAGE REJECT, INITIATOR ERROR, and ABORT.

## Important APIs, Types, and Functions

Internal helpers are `mqe_alloc()` and `mqe_free()`, which manage the queue's fixed free list. Exported APIs are `msgqueue_initialise()`, `msgqueue_free()`, `msgqueue_msglength()`, `msgqueue_getmsg()`, `msgqueue_addmsg()`, and `msgqueue_flush()`.

## Control Flow

Initialization links the embedded `entries[NR_MESSAGES]` array into a free list and clears the active queue. `msgqueue_addmsg()` pops a free entry, copies variadic message bytes into the fixed 8-byte message buffer, sets length and FIFO marker, and appends to the active list. Consumers call `msgqueue_msglength()` to program transfer counts and `msgqueue_getmsg()` by index to emit messages. Flush returns all active entries to the free list.

## State and Persistence Behavior

State is entirely embedded in `MsgQueue_t`: active list head, free-list head, and four preallocated entries. There is no dynamic allocation and no durable persistence. `msgqueue_free()` is intentionally empty because no external resources are owned.

## Dependencies and Integration Points

The module depends on standard kernel module headers and `msgqueue.h`. It exports its functions for use by `acornscsi.c` and `fas216.c`.

## Risks and Edge Cases

`msgqueue_addmsg()` does not validate `length <= sizeof(msg.msg)`, so callers must never enqueue messages longer than eight bytes. The queue capacity is four messages; overflow returns false and callers often do not check. There is no internal locking, so callers must serialize access through their host locks or interrupt exclusion. Variadic arguments are read as `unsigned int`, matching integer promotion for byte constants.

## Test Signals

Tests should cover initialization, four-message capacity, overflow return, flush reuse, indexed retrieval, total length calculation, zero-length messages if callers ever use them, and an audit that all current message lengths are at most eight bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.h -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.h

## Purpose

`msgqueue.h` declares the fixed-size message queue used by ARM SCSI protocol engines for outgoing SCSI message phases. It provides the shared data structures and function prototypes implemented in `msgqueue.c`.

## Important APIs, Types, and Functions

`struct message` stores up to eight message bytes, length, and a FIFO position marker. `struct msgqueue_entry` links a message into either the active or free list. `MsgQueue_t` contains active and free heads plus `NR_MESSAGES` embedded entries. Public functions are `msgqueue_initialise`, `msgqueue_free`, `msgqueue_msglength`, `msgqueue_getmsg`, `msgqueue_addmsg`, and `msgqueue_flush`.

## Control Flow

Callers initialize a queue per host, add one or more messages before message-out phases, ask for total message length and indexed entries while programming the chip FIFO, and flush the queue when the message sequence is no longer needed or when reset/error handling starts.

## State and Persistence Behavior

The queue is fixed, in-memory, and host-owned. It does not allocate memory dynamically and has no persistence. The `fifo` field is written by protocol engines to remember where a message landed in a chip FIFO for later MESSAGE REJECT attribution.

## Dependencies and Integration Points

The header is consumed by `msgqueue.c`, `acornscsi.h`, and `fas216.h`. It has no kernel includes of its own and relies on including translation units to provide needed base types.

## Risks and Edge Cases

The fixed four-entry, eight-byte-message design is small but brittle. Callers must handle `msgqueue_addmsg()` failure and must not enqueue longer messages. Because there is no locking, misuse from concurrent interrupt and queue contexts could corrupt the linked lists.

## Test Signals

Validation should check ABI expectations for `NR_MESSAGES`, message byte capacity, FIFO marker behavior under MESSAGE REJECT, and all current call sites' message lengths and failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/msgqueue.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/oak.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/oak.c

## Purpose

`oak.c` implements the Oak 16-bit SCSI expansion-card driver using the generic NCR5380 core. It provides board-specific register access, partial pseudo-DMA helpers, host-template glue, probe/remove, and module registration.

## Important APIs, Types, and Functions

The file specializes NCR5380 through macros for register read/write, queue command, info, and pseudo-DMA setup. Card-specific functions are `oakscsi_pread()`, `oakscsi_pwrite()`, `oakscsi_probe()`, `oakscsi_remove()`, `oakscsi_init()`, and `oakscsi_exit()`. The included `../NCR5380.c` supplies most SCSI protocol behavior.

## Control Flow

Probe claims the card, allocates an NCR5380 host, maps MEMC space, configures no IRQ, initializes the NCR5380 core with DMA fixup and late setup flags, maybe resets the bus, adds the host, and scans. Since `host->irq = NO_IRQ`, behavior is polling-oriented through the NCR5380 core.

`oakscsi_pread()` polls a status register for ready/error bits, reads up to 128 words at a time from the data port, handles trailing bytes, and times out on error. `oakscsi_pwrite()` currently logs the request and then loops forever polling status, never transferring or returning.

## State and Persistence Behavior

Runtime state is NCR5380 hostdata with an MMIO base. The file has no durable settings and no additional private state beyond the generic core.

## Dependencies and Integration Points

The driver depends on ARM ecard APIs, MMIO helpers, Linux SCSI host APIs, and the generic NCR5380 implementation included directly. It matches `MANU_OAK/PROD_OAK_SCSI`.

## Risks and Edge Cases

The write pseudo-DMA path is nonfunctional and can hang indefinitely. This is the dominant risk and should make write-capable use unsafe unless the NCR5380 core never selects that path for writes. `oakscsi_pread()` subtracts two bytes in the trailing branch even when only one byte remained, which can underflow `len` in local accounting after the final byte. The driver has no IRQ and limited error recovery visibility.

## Test Signals

Test probe/scan, read-only workloads, timeout behavior in `oakscsi_pread()`, any write command path to confirm it is blocked or hangs, clean removal, and NCR5380 abort/host reset behavior with `NO_IRQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/oak.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/powertec.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/arm/powertec.c

## Purpose

`powertec.c` implements the PowerTec SCSI expansion-card driver. It wraps the generic FAS216 core with PowerTec-specific register offsets, IRQ control, terminator control, optional real DMA setup, sysfs/proc reporting, and expansion-card lifecycle.

## Important APIs, Types, and Functions

`struct powertec_info` embeds `FAS216_Info`, card/base pointers, terminator latch state, and a fixed SG array. Key functions are `powertecscsi_irqenable()`, `powertecscsi_irqdisable()`, `powertecscsi_terminator_ctl()`, `powertecscsi_intr()`, `powertecscsi_dma_setup()`, `powertecscsi_dma_stop()`, `powertecscsi_info()`, `powertecscsi_set_proc_info()`, sysfs `bus_term` show/store handlers, `powertecscsi_probe()`, and `powertecscsi_remove()`.

## Control Flow

Probe claims resources, maps IOCFAST space, allocates a host, sets initial termination from `term[]`, fills FAS216 hardware/timing fields and DMA callbacks, installs ecard IRQ ops, creates the `bus_term` device attribute, initializes FAS216, requests IRQ and optional DMA, enables `FASCAP_DMA` when DMA is available, and calls `fas216_add()`. Runtime SCSI flow is handled by `fas216_queue_command()` and `fas216_intr()`.

DMA setup only uses real DMA when the FAS216 capability bit is set and the core requires `fasdma_real_all`; otherwise it returns `fasdma_pio`. Unlike EESOX/Cumana II, `info->info.dma.pseudo` is NULL, so no pseudo-DMA fallback is advertised.

## State and Persistence Behavior

Runtime state includes the terminator latch, fixed SG array, optional DMA channel, and embedded FAS216 queues/device/transfer state. The module parameter `term[]` controls initial termination by slot but changes through sysfs/proc are live only.

## Dependencies and Integration Points

The driver depends on ecard APIs, FAS216 APIs, `arm_scsi.h`, ARM DMA APIs, Linux device attributes, and SCSI host-template callbacks. It matches `MANU_ALSYSTEMS/PROD_ALSYS_SCSIATAPI`.

## Risks and Edge Cases

As with other DMA wrappers, `dma_map_sg()` return value and unmap behavior are risk points. `device_create_file()` return is ignored. Termination control is not protected by `host_lock`, unlike EESOX, so concurrent sysfs/proc and IRQ paths should be reviewed. If real DMA is unavailable, the FAS216 core falls back to byte PIO, which may be slow but avoids a NULL pseudo callback because `fasdma_pio` is returned.

## Test Signals

Validate initial and live termination control, IRQ enable/disable, probe with DMA available and unavailable, real DMA transfers requiring `fasdma_real_all`, PIO fallback, FAS216 sync/disconnect/request-sense behavior, sysfs cleanup, and failure unwinding for IRQ/DMA/host resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/arm/powertec.c -->
