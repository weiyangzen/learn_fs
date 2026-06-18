<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.c -->
# sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.c

## Purpose

`esp_scsi.c` is the generic core for NCR/Symbios ESP-family SCSI host adapters. Platform front-end drivers provide register/DMA operations and hardware resources; this file provides chip reset/probing, SCSI command queueing, target/LUN tag management, SCSI phase/event handling, DMA progression, synchronous/wide negotiation, reselection/disconnect support, autosense, interrupt handling, SCSI error handling, and SPI transport integration.

## Important APIs, Types, and Functions

Exported symbols are `scsi_esp_template`, `scsi_esp_register()`, `scsi_esp_unregister()`, `scsi_esp_intr()`, `scsi_esp_cmd()`, and, when PIO support is enabled, `esp_send_pio_cmd()`. Front-end drivers allocate a `Scsi_Host` using `scsi_esp_template`, initialize `struct esp`, install `struct esp_driver_ops`, map command DMA memory, register `scsi_esp_intr()` as the interrupt handler, then call `scsi_esp_register()`.

Important internal groups include chip setup (`esp_set_clock_params()`, `esp_get_revision()`, `esp_reset_esp()`, `esp_bootup_reset()`), DMA state (`esp_map_dma()`, `esp_unmap_dma()`, `esp_cur_dma_addr()`, `esp_cur_dma_len()`, `esp_advance_dma()`, `esp_dma_length_limit()`), command scheduling (`esp_queuecommand_lck()`, `esp_get_ent()`, `esp_put_ent()`, `find_and_prep_issuable_command()`, `esp_maybe_execute_command()`), completion (`esp_cmd_is_done()`), phase engine (`esp_process_event()`), interrupt handling (`__esp_interrupt()`, `scsi_esp_intr()`), reconnect handling (`esp_reconnect()`, `esp_reconnect_with_tag()`), negotiation (`esp_setsync()`, `esp_msgin_sdtr()`, `esp_msgin_wdtr()`, `esp_msgin_reject()`), and EH (`esp_eh_abort_handler()`, `esp_eh_bus_reset_handler()`, `esp_eh_host_reset_handler()`).

## Control Flow

Registration sets host transport state, defaults tag count, sets max LUN and per-LUN command count, computes clock conversion/timeout/sync defaults, probes chip revision by config register behavior and ID family, initializes lists and target negotiation goals, resets the ESP and SCSI bus, waits for the bus reset settle time, adds the SCSI host, and scans targets.

`esp_queuecommand_lck()` allocates or reuses an `esp_cmd_entry`, attaches the `scsi_cmnd`, queues it, and calls `esp_maybe_execute_command()`. If no command is active and the chip is not resetting, command selection chooses an issuable entry whose LUN tag rules allow dispatch. `esp_maybe_execute_command()` maps DMA, saves data pointers, builds identify/tag/negotiation messages and CDB bytes, chooses select-with-ATN, select-and-stop, or select-with-ATN3, programs target sync/config registers, and starts the command via FIFO or platform DMA.

Interrupts drive the SCSI phase machine. `scsi_esp_intr()` takes `host_lock`, checks front-end `irq_pending()`, calls `__esp_interrupt()`, and loops briefly for quick follow-up interrupts. `__esp_interrupt()` snapshots status, sequence, and interrupt registers, detects reset/gross/spurious/DMA errors, handles FASHME FIFO snapshots, finishes selection or reconnects on reselection, then repeatedly calls `esp_process_event()`. The event engine transitions through command, data-in/out, data-done, status, message-in/out, free-bus, check-phase, and reset events. It starts DMA transfers with chip/front-end limits, computes actual bytes sent from counters/FIFO residuals, advances scatterlist state, processes SCSI messages, handles disconnects by clearing `active_cmd`, and completes commands or launches autosense on CHECK CONDITION.

Autosense is local to the driver. When a command completes with CHECK CONDITION and is not already autosensing, the entry is marked `ESP_CMD_FLAG_AUTOSENSE`, a REQUEST SENSE command is built against the same target/LUN and sense buffer, and completion restores CHECK CONDITION semantics while providing sense data to the original command.

EH abort first tries to remove a still-queued command. For the active command it sends an ABORT_TASK_SET message by asserting ATN and waits up to five seconds for completion. Disconnected commands are not directly aborted and are left to bus/host reset. Bus reset issues ESP SCSI bus reset and waits for reset completion; host reset performs a bootup chip reset and cleanup.

## State and Persistence Behavior

All state is volatile in memory and hardware registers. `struct esp` tracks register/DMA resources, front-end operations, active command, queued/active lists, command entry pool, command DMA buffer, data DMA length, last hardware status registers, per-target negotiation state, FIFO snapshot, event log, message buffers, chip revision, flags, clock parameters, selection/event state, and EH reset completion. `struct esp_target_data` stores negotiated and desired sync/wide state per target. `struct esp_lun_data` stores the non-tagged command, tagged command table, tag count, and hold state per LUN. `struct esp_cmd_priv` stores scatterlist progression per SCSI command.

Negotiation state persists across commands until reset or transport settings change. Reset cleanup forces renegotiation by clearing per-target sync/wide bits and setting `ESP_TGT_CHECK_NEGO`. The event log is an in-memory ring used for diagnostics and dumped on errors.

## Dependencies and Integration Points

The file depends on Linux SCSI mid-layer APIs, SCSI transport SPI domain validation and attributes, DMA mapping APIs, host locks, completions, module parameters, and platform-specific ESP front-end operations. It exports a reusable core for platform drivers such as SBus, Mac, or other ESP-family adapters. Integration contracts with front-ends are strict: `irq_pending()`, `send_dma_cmd()`, `dma_error()`, `dma_drain()`, `dma_invalidate()`, register access, and optional DMA length limiting must accurately reflect hardware behavior.

## Risks and Edge Cases

The code is a hardware state machine with many chip-revision quirks. Wrong front-end IRQ or DMA-error reporting can cause missed interrupts, spurious resets, or data corruption. Reselection with tags is polling-heavy and assumes quick follow-up interrupts; timeouts force reset. DMA byte accounting depends on ESP counters, FIFO state, wide mode, residual-byte quirks, and front-end drain/invalidate semantics. Disconnected command abort is not implemented, so error recovery may escalate to bus reset. The PIO path casts DMA addresses to CPU pointers and is only valid when the front-end sets `ESP_FLAG_NO_DMA_MAP` and supplies virtual-address style transfers. Heavy debug logging and command-log dumps can be noisy under error storms.

## Test Signals

Important signals include registration on each supported chip revision, correct clock/timeout values, boot reset and bus settle, SCSI scan, basic CDB dispatch, scatterlist DMA progression across segment and 24-bit/16-bit boundaries, data-in/out under FIFO and DMA modes, disconnect/reconnect with and without tags, sync and wide negotiation including message reject fallback, autosense on CHECK CONDITION, queue-full feedback, abort of queued and active commands, bus reset and host reset cleanup, FASHME FIFO handling, ESP100/FAS/AM53c974 quirks, PIO transfers when configured, and front-end fault injection for DMA error, spurious IRQ, illegal command, gross error, and reselection timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/scsi/esp_scsi.c -->
