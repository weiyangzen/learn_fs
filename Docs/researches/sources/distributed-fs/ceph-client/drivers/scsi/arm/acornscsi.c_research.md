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
