<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-topcliff-pch.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-topcliff-pch.c

## Purpose

`spi-topcliff-pch.c` is the SPI host driver for Intel EG20T Topcliff PCH and related LAPIS/ROHM ML7213, ML7223, and ML7831 IOH devices. It binds as a PCI driver, creates one or more child platform devices for individual SPI channels, and registers each channel as a Linux `spi_controller`.

The driver supports 8-bit and 16-bit words, up to 255 chip selects, programmable SPI mode bits, and optional PCH DMA engine transfers through the `use_dma` module parameter. It is an older pre-`transfer_one` style implementation: SPI messages are queued on a private list and processed by a work item, with completion reported through SPI message callbacks.

## Important APIs, Types, and Functions

Key hardware definitions cover register offsets (`PCH_SPCR`, `PCH_SPBRR`, `PCH_SPSR`, `PCH_SPDWR`, `PCH_SPDRR`, `PCH_SSNXCR`, `PCH_SRST`), FIFO depth and thresholds, interrupt enable/status bits, chip-select values, clock constants, and PCI IDs.

`struct pch_spi_data` is the per-channel state: MMIO base, `spi_controller`, work item, wait queue, message queue, active message/transfer pointers, transfer indices, temporary packet buffers, current chip select, channel id, DMA state, IRQ state, and lifecycle status. `struct pch_spi_dma_ctrl` tracks PCH DMA channels, descriptors, scatterlists, coherent buffers, and DMA slave parameters. `struct pch_spi_board_data` and `struct pch_pd_dev_save` bridge the PCI device to platform children.

Core register helpers are `pch_spi_writereg()`, `pch_spi_readreg()`, and `pch_spi_setclr_reg()`. Hardware setup helpers include `pch_spi_reset()`, `pch_spi_set_host_mode()`, `pch_spi_clear_fifo()`, `pch_spi_set_baud_rate()`, `pch_spi_set_bits_per_word()`, and `pch_spi_setup_transfer()`.

The SPI framework entry is `pch_spi_transfer()`, which queues messages and schedules `pch_spi_process_messages()`. Non-DMA transfers use `pch_spi_set_tx()`, `pch_spi_set_ir()`, `pch_spi_handler()`, `pch_spi_handler_sub()`, and `pch_spi_copy_rx_data()`. DMA transfers use `pch_spi_request_dma()`, `pch_spi_handle_dma()`, `pch_spi_start_transfer()`, `pch_dma_rx_complete()`, `pch_spi_copy_rx_data_for_dma()`, and `pch_spi_release_dma()`.

Lifecycle functions are split between PCI and platform layers: `pch_spi_probe()` creates child platform devices according to PCI `driver_data`; `pch_spi_pd_probe()` allocates/registers the SPI controller; remove and PM paths tear down or suspend both layers.

## Control Flow

PCI probe allocates shared board data, requests PCI BAR regions, enables the PCI function, then creates one platform device per SPI channel. Platform probe allocates a `spi_controller`, maps the PCI MMIO BAR, offsets the channel register window by `PCH_ADDRESS_SIZE * id`, initializes controller capabilities, resets the channel, requests the shared IRQ, optionally allocates coherent DMA buffers, and registers the SPI controller.

SPI clients call `host->transfer`, which rejects transfers during suspend or removal, initializes message status, appends the message to `data->queue` under `data->lock`, and schedules the worker. The worker flushes the queue if suspend/removal is active; otherwise it removes one message, selects/configures the target, optionally acquires DMA channels, asserts chip select, and iterates each `spi_transfer`.

In PIO mode, the worker allocates 16-bit temporary TX/RX packet arrays, normalizes user buffers into words, writes up to FIFO depth to the TX register, enables SPI and interrupts, and waits on `data->wait`. The IRQ handler acknowledges status, drains RX FIFO entries, refills TX as RX progresses, disables RX interrupts near the end, and wakes the worker when final interrupt reports TX/RX completion. The worker then copies received words back to the caller buffer, frees temporary buffers, runs transfer delay handling, updates message length, and completes the message when the transfer list ends.

In DMA mode, the worker requests paired PCH DMA channels for the channel id, copies the caller TX buffer into a coherent buffer, builds RX and TX scatterlists in chunks shaped around `PCH_DMA_TRANS_SIZE`, programs FIFO thresholds, submits RX then TX DMA descriptors, enables SPI, and waits for the RX DMA callback. After completion it syncs coherent scatterlists for CPU, clears/free scatterlists, resets FIFO/interrupt state, copies RX data back, and handles messages larger than `PCH_BUF_SIZE` as repeated chunks.

PCI and platform suspend are coordinated through `board_dat->suspend_sts`. The PCI PM callback flips the shared flag; platform suspend waits for current processing to stop, disables interrupts, resets hardware, and frees the IRQ. Resume requests the IRQ again and reinitializes hardware.

## State and Persistence Behavior

The driver has no file-backed persistence. Persistent external effects are SPI bus transactions to attached devices and hardware register state in the controller.

Long-lived kernel state is held in `struct pch_spi_data` for each channel, `struct pch_spi_board_data` for the PCI function, coherent DMA buffers, and child platform devices. `status`, `suspend_sts`, `irq_reg_sts`, `bcurrent_msg_processing`, `transfer_complete`, and `transfer_active` are the main lifecycle/concurrency flags.

Per-transfer state is stored in `cur_trans`, `current_msg`, transfer indices, `bpw_len`, temporary PIO packet buffers, or DMA descriptors/scatterlists. DMA channels are requested per message and released after the message finishes. The controller's baud rate, word size, polarity, phase, FIFO thresholds, interrupt enables, and chip-select register are reprogrammed for active transfers.

## Dependencies and Integration Points

The file depends on the Linux PCI, platform-device, SPI controller, waitqueue, workqueue, interrupt, DMAengine, PCH DMA, coherent DMA, and PM subsystems. Device matching is via PCI IDs; the module registers both a PCI driver (`pch_spi`) and a platform driver (`pch-spi`).

SPI integration is through `spi_alloc_host()`, `spi_register_controller()`, `host->transfer`, controller mode bits, word-size mask, chip-select count, and message callbacks. DMA integration is tightly coupled to the PCH DMA slave filter and channel numbering convention `ch * 2` for TX and `ch * 2 + 1` for RX.

## Risks and Edge Cases

The code uses an older custom message queue instead of SPI core queued transfer helpers, so locking, callbacks, suspend, and remove races are locally managed. Message callbacks can be invoked while queue locks are being dropped and reacquired, which needs careful lock-order testing.

PIO allocation uses `cur_trans->len * sizeof(u16)` even for 8-bit transfers, and `bpw_len` derives from `len / (bpw / 8)`. Odd byte counts with 16-bit words, zero lengths, and invalid word-size combinations depend on SPI core validation. Allocation failure flushes all queued messages, not just the current transfer.

The DMA path mutates `cur_trans->len` while chunking and also advances `cur_trans->rx_buf` in `pch_spi_copy_rx_data_for_dma()` before restoring it at message end. Any caller or debug code observing the transfer during processing could see transient state. Error paths inside `pch_spi_handle_dma()` can return after allocating one scatterlist or descriptor without consistently freeing everything until later cleanup paths.

`pch_alloc_dma_buf()` can allocate TX, fail RX, and return `-ENOMEM`; later cleanup frees any nonzero allocation, but the failure path should be tested. `pch_spi_release_dma()` calls `pci_dev_put(dma->dma_dev)` assuming a successful `pci_get_slot()`. IRQ handling returns `IRQ_NONE` for DMA mode even though the shared IRQ may still carry controller status.

MMIO mapping is offset by changing `data->io_remap_addr` after `pci_iomap()`, then `pci_iounmap()` is later called with the adjusted pointer. That is a notable resource-management risk because unmap APIs generally expect the original mapping base.

## Test Signals

Build coverage should include both `use_dma=0` and `use_dma=1`, PCI IDs with one and two channels, 8-bit and 16-bit word sizes, mode 0-3, LSB-first, and high chip-select numbers.

Runtime tests should cover short PIO transfers, FIFO-depth and larger PIO transfers, DMA transfers below/equal/above `PCH_BUF_SIZE`, TX-only, RX-only, full-duplex, zero-length transfers, delay handling, queueing multiple messages, and suspend/remove while queued or active. Fault injection should target IRQ request failure, DMA channel request failure, coherent allocation failure, DMA descriptor prep failure, timeout in `pch_spi_start_transfer()`, overrun interrupt status, and stale queue flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-topcliff-pch.c -->
