# subset-b-005391 Research

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-uniphier.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-uniphier.c

## Purpose

`spi-uniphier.c` is a platform SPI controller driver for Socionext UniPhier SCSSI hardware. It registers a single-chip-select SPI host that can execute transfers by polling, interrupt completion, or DMA depending on transfer size and available DMA channels.

The driver programs SSI clock/frame/data-size registers per transfer, supports SPI modes 0-3, `SPI_CS_HIGH`, `SPI_LSB_FIRST`, word sizes from 1 to 32 bits, and full-duplex semantics forced by `SPI_CONTROLLER_MUST_RX | SPI_CONTROLLER_MUST_TX`.

## Important APIs, Types, and Functions

`struct uniphier_spi_priv` contains MMIO base, physical base for DMA slave addresses, clock, controller pointer, completion, error status, TX/RX byte counters, user buffer pointers, DMA busy bitmask, and cached mode/word/speed parameters.

Register definitions cover SSI control, clock settings, TX/RX word-size registers, frame polarity/start, status, interrupt enable/status/clear, FIFO control, and shared TX/RX data register. `bytes_per_word()` maps bit width to 1, 2, or 4 bytes.

Configuration helpers are `uniphier_spi_set_mode()`, `uniphier_spi_set_transfer_size()`, `uniphier_spi_set_baudrate()`, and `uniphier_spi_setup_transfer()`. FIFO helpers are `uniphier_spi_send()`, `uniphier_spi_recv()`, `uniphier_spi_set_fifo_threshold()`, and `uniphier_spi_fill_tx_fifo()`.

Transfer paths are `uniphier_spi_transfer_one_poll()`, `uniphier_spi_transfer_one_irq()`, and `uniphier_spi_transfer_one_dma()`, selected by `uniphier_spi_transfer_one()`. DMA support is advertised by `uniphier_spi_can_dma()` and completed by `uniphier_spi_dma_rxcb()` / `uniphier_spi_dma_txcb()`. Error and hardware lifecycle hooks are `uniphier_spi_handle_err()`, `uniphier_spi_prepare_transfer_hardware()`, and `uniphier_spi_unprepare_transfer_hardware()`.

`uniphier_spi_probe()` maps resources, enables the clock, requests IRQ, optionally obtains DMA channels, fills controller callbacks, and registers the controller.

## Control Flow

Probe allocates a SPI host, maps one MMIO resource, records its physical address for DMA, enables the clock, requests the platform IRQ, initializes completion, computes min/max speed from the clock divider limits, requests optional `"tx"` and `"rx"` DMA channels, sets `max_dma_len` from DMA burst caps, and registers the controller.

For each transfer, `uniphier_spi_transfer_one()` ignores zero-length transfers, calls `uniphier_spi_setup_transfer()` to cache buffers and counters, reprograms mode/size/speed only when the cached value changed, and resets FIFOs. If DMA is usable and the transfer exceeds FIFO depth in words, the DMA path is used. Otherwise, the function estimates whether the transfer fits within `SSI_POLL_TIMEOUT_US`; short transfers use polling and longer ones use IRQ completion.

Polling repeatedly fills the TX FIFO and drains RX as words become readable. If the polling loop cannot observe RX readiness within the microsecond budget, it falls back to the IRQ path. The IRQ path fills the initial FIFO, enables receive-complete and overrun interrupts, waits for completion, disables interrupts, and returns the collected error.

DMA configures FIFO burst threshold, programs DMA slave configs to SSI TX/RX data register addresses, prepares RX and TX scatter-gather descriptors only for buffers present in the transfer, enables DMA request interrupts, marks busy bits atomically, submits descriptors, and returns nonzero to tell the SPI core that completion is asynchronous. Each DMA callback clears its busy bit and finalizes the current transfer when the opposite direction has also completed.

The IRQ handler acknowledges all relevant interrupt causes, handles receive overrun as `-EIO`, drains RX FIFO on receive-complete status, validates FIFO/counter consistency, refills TX FIFO for the next chunk, and completes when all RX bytes are consumed.

## State and Persistence Behavior

There is no file-backed persistence. Persistent hardware state is limited to SSI registers while the controller is prepared. The driver caches the last configured `mode`, `bits_per_word`, and `speed_hz` to avoid redundant register writes between transfers.

Per-transfer state lives in `tx_bytes`, `rx_bytes`, `tx_buf`, `rx_buf`, `error`, and the `xfer_done` completion. DMA state is tracked with `dma_busy`, where TX and RX callbacks independently clear bits. On error, the driver disables the controller, flushes FIFOs, disables interrupts, and terminates active DMA channels.

## Dependencies and Integration Points

The driver depends on platform resources, device tree compatible `"socionext,uniphier-scssi"`, MMIO, clocks, IRQs, DMAengine, Linux completions, unaligned little-endian helpers, and the SPI controller API.

SPI integration uses `transfer_one`, `set_cs`, prepare/unprepare hardware hooks, `handle_err`, `can_dma`, `max_dma_len`, DMA channels attached to `host->dma_tx` / `host->dma_rx`, and `spi_finalize_current_transfer()` for asynchronous DMA.

## Risks and Edge Cases

`uniphier_spi_set_baudrate()` rounds the divider up to an even value but does not explicitly clamp to the documented 4..254 range before writing the masked low byte. The controller's min/max speed fields should keep callers inside range, but direct or malformed transfer speeds still deserve validation.

The cached-parameter logic sets `is_save_param = false` after reprogramming mode, then sets it true at the end. This works, but the unusual assignment makes future changes easy to misread.

DMA callbacks call `spi_finalize_current_transfer()` from DMA callback context after disabling request interrupts. Races between RX and TX callbacks are mediated by atomic bits; tests should cover TX-only, RX-only, and full-duplex DMA. Error cleanup uses `dmaengine_terminate_async()`, so completion ordering after an error path is worth stress testing.

The polling fallback reuses the same transfer state after a partial polling attempt. That is intentional: bytes already sent/received remain reflected in counters, and the IRQ path continues. Regression tests should ensure fallback does not duplicate or drop words.

## Test Signals

Useful tests include build coverage with DMA enabled/disabled, all SPI modes, `SPI_CS_HIGH`, `SPI_LSB_FIRST`, word sizes 1, 8, 16, 24, and 32, and transfers around the FIFO depth and polling threshold.

Runtime signals should cover polling completion, polling-to-IRQ fallback, IRQ overrun handling, DMA RX-only/TX-only/full-duplex, DMA channel absence, DMA `-EPROBE_DEFER`, suspend/error cleanup through `handle_err`, clock-rate derived speed limits, and removal after active DMA resources are allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-uniphier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-virtio.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-virtio.c

## Purpose

`spi-virtio.c` is the Linux SPI host driver for the virtio SPI device. It exposes a virtio-provided SPI controller to the SPI core and translates each `spi_transfer` into one virtqueue request containing a `spi_transfer_head`, optional TX payload, optional RX payload, and result status.

The implementation is deliberately simple: it supports only one in-flight transfer per controller and waits synchronously for virtqueue completion inside `transfer_one`.

## Important APIs, Types, and Functions

`struct virtio_spi_priv` stores the virtio device, single request virtqueue, and cached config fields (`mode_func_supported`, `max_freq_hz`). `struct virtio_spi_req` owns one transfer's completion, TX/RX buffer pointers, virtio transfer header, and result structure.

`virtio_spi_read_config()` reads virtio config space (`struct virtio_spi_config`) and maps supported mode/function bits to SPI controller `mode_bits`, chip-select count, bits-per-word mask, dual/quad/octal TX/RX support, loopback, and max frequency.

`virtio_spi_set_delays()` converts Linux SPI delay fields into nanoseconds for the virtio header: CS setup, max of device/transfer word delay, transfer delay plus CS hold, and CS inactive plus CS-change delay.

`virtio_spi_transfer_one()` builds the virtqueue scatter-gather list and translates virtio result codes to Linux errors. `virtio_spi_msg_done()` completes requests returned by `virtqueue_get_buf()`. `virtio_spi_find_vqs()` and `virtio_spi_del_vq()` manage the single queue. PM support is handled by `virtio_spi_freeze()` and `virtio_spi_restore()`.

## Control Flow

Probe allocates a devm SPI host, stores private state in `vdev->priv`, reads virtio config to size and advertise the controller, installs `transfer_one`, creates the single virtqueue named `"spi-rq"`, registers a devm cleanup action that resets the device and deletes queues, and registers the SPI controller.

For a transfer, the driver allocates a request, initializes the virtio header from the SPI device and transfer fields, asserts compile-time equality between Linux SPI mode constants and virtio constants, handles loopback mapping, writes requested frequency, converts all delay fields, and prepares scatterlist entries. The outgoing list always contains the transfer header and optionally the TX payload. The incoming list optionally contains the RX payload and always contains the result.

The request is submitted with `virtqueue_add_sgs()`, the queue is kicked, and the thread waits for `virtio_spi_msg_done()` to complete the request. After completion, `VIRTIO_SPI_TRANS_OK` returns success, `VIRTIO_SPI_PARAM_ERR` maps to `-EINVAL`, and other errors map to `-EIO`. On error the driver's current SPI message status is updated.

Freeze suspends the SPI controller and deletes virtqueues after resetting the virtio device. Restore recreates the virtqueue and resumes the SPI controller.

## State and Persistence Behavior

There is no persistent local storage. The controller state is virtio config space plus the active virtqueue. `max_freq_hz` is cached but not directly assigned to `ctrl->max_speed_hz` in this implementation. Each request is heap-allocated for one transfer and freed automatically at function exit.

Transfers can modify remote device state through the virtio backend and attached SPI target devices. The Linux driver itself stores no durable transaction log or replay state.

## Dependencies and Integration Points

The driver depends on the virtio core, virtqueue APIs, `linux/virtio_spi.h` ABI definitions, completions, scatterlists, and the SPI controller framework.

The main integration contract is the virtio SPI device ABI: header fields must be little-endian where specified, mode constants must match Linux SPI constants, result codes must be interpreted exactly, and the backend must return the request buffer for completion.

## Risks and Edge Cases

The synchronous one-transfer model is simple but limits queue depth and throughput. A hung or non-returning backend can block the transfer path indefinitely because `wait_for_completion()` has no timeout.

Delay conversion failures abort the transfer, but addition of delay components can overflow `int` before conversion to little-endian `u32` if extreme values are accepted upstream. The driver also caches `max_freq_hz` without enforcing it in `transfer_one`.

The `sgs` array ordering is subtle: when RX payload exists it is assigned at `sgs[outcnt]` and `incnt` is incremented, while the result is assigned at `sgs[outcnt + incnt]`. This is correct for virtqueue split output/input counts but should be preserved carefully.

Virtqueue deletion is registered with devm and also used in freeze; restore recreates queues. PM tests should ensure the devm cleanup action does not double-delete a queue after freeze/restore sequences.

## Test Signals

Tests should cover virtio config parsing for chip-select counts, word masks, CPOL/CPHA, CS high, LSB first, loopback, dual/quad/octal modes, and max frequency. Transfer tests should include TX-only, RX-only, full-duplex, zero-length, delay conversion fields, chip-select ids, loopback mode, and virtio result codes OK, parameter error, transfer error, and unknown.

Fault tests should cover allocation failure, `virtqueue_add_sgs()` failure, backend non-completion, freeze/restore during idle and after registered devices, and queue recreation after restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-virtio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-wpcm-fiu.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-wpcm-fiu.c

## Purpose

`spi-wpcm-fiu.c` is a SPI memory controller driver for the Nuvoton WPCM450 Flash Interface Unit. It implements `spi-mem` operations over the FIU's User Mode Access (UMA) registers and supports direct mapped flash reads through the FIU memory window.

The hardware can handle only small UMA data payloads and has special behavior for some flash commands, so the driver classifies operations into supported shapes and executes multi-step sequences where needed.

## Important APIs, Types, and Functions

`struct wpcm_fiu_spi` stores device, clock, control register mapping, direct memory window mapping/size, and optional SHM syscon regmap used to stall host flash accesses during UMA transfers.

Low-level UMA helpers are `wpcm_fiu_set_opcode()`, `wpcm_fiu_set_addr()`, `wpcm_fiu_set_data()`, `wpcm_fiu_get_data()`, `wpcm_fiu_do_uma()`, `wpcm_fiu_ects_assert()`, and `wpcm_fiu_ects_deassert()`.

`struct wpcm_fiu_op_shape` binds a matcher to an executor. Supported shapes are normal command/address/no-dummy operations with up to 4 data bytes, a fast-read matcher that currently returns `-EINVAL`, 4-byte-address operations split into two UMA cycles, RDID six-byte reads split into two reads, and operations with dummy bytes split across asserted chip select.

SPI memory callbacks are `wpcm_fiu_supports_op()`, `wpcm_fiu_exec_op()`, `wpcm_fiu_adjust_op_size()`, `wpcm_fiu_dirmap_create()`, and `wpcm_fiu_direct_read()`. `wpcm_fiu_hw_init()` configures the flash memory window and deasserts manual chip selects. `wpcm_fiu_probe()` maps resources, enables the clock, initializes hardware, fills `mem_ops`, and registers the controller.

## Control Flow

Probe allocates a SPI host, maps `"control"` registers and `"memory"` flash window, enables the FIU clock, optionally resolves a `"nuvoton,shm"` syscon, initializes burst/window registers, sets all manual chip selects deasserted, and registers a four-chip-select SPI memory controller. The controller min and max speeds are both the AHB3 clock because the FIU has no divider.

Before executing a SPI memory operation, `supports_op` first asks the SPI MEM core for default support, rejects DTR and multi-bit bus widths, then finds a matching shape. `adjust_op_size` clamps data payloads to 4 bytes because UMA has four data registers.

`exec_op` stalls host flash-memory accesses through SHM when available, finds the shape, and executes it. Normal operations write opcode/address/data registers, run one UMA command with address/write/data-size flags, and read data registers on input. Four-byte addressing asserts manual chip select and emits the high three address bytes as one UMA phase, then uses the low address byte as a pseudo opcode for the second phase. RDID performs two reads because FIU can read only up to four bytes. Dummy-byte operations assert chip select, send opcode/address plus dummy bytes as a write-like phase, then run a read phase.

Direct mapping validates that the operation is read-only, the requested mapping does not cross the 16 MiB per-chip window, and the requested chip-select window exists in the mapped memory resource. Direct reads copy from the appropriate `cs * 16 MiB + offset` MMIO memory window.

## State and Persistence Behavior

The driver keeps only volatile controller mappings and optional SHM regmap state. It writes FIU configuration registers during probe and UMA control/data registers per operation. SPI flash contents can be changed by write/erase commands issued through UMA, but the driver itself stores no persistent metadata.

Manual chip-select state is controlled by the ECTS register during multi-phase operations. Host memory access stalling is intended to be temporary around UMA transfers so the BMC host side does not collide with software-controlled accesses.

## Dependencies and Integration Points

The driver depends on platform resources named `"control"` and `"memory"`, device tree compatible `"nuvoton,wpcm450-fiu"`, clocks, MMIO byte accessors, regmap/syscon, and the SPI MEM framework.

It integrates with SPI NOR or other SPI memory clients through `spi_controller_mem_ops`, including both `exec_op` and direct-map reads. The optional SHM syscon integration updates `SHM_FLASH_SIZE_STALL_HOST`.

## Risks and Edge Cases

`wpcm_fiu_exec_op()` stalls host access before executing a matching shape but returns directly from `shape->exec()` without unstalling the host. The unstall path is only reached when no shape is found. That is a strong bug signal unless some external mechanism clears the stall bit.

Several shape executors ignore return values from `wpcm_fiu_do_uma()`, especially multi-phase 4-byte address, RDID, and dummy paths. A timed-out UMA phase can still produce success and stale data.

`wpcm_fiu_fast_read_match()` accepts opcode `0x0b`, but its executor always returns `-EINVAL`; because `supports_op()` only checks for a shape, the core may choose an operation that later fails. This is a mismatch between capability advertisement and execution.

The operation-shape model only supports single-bit bus widths, no DTR, small payloads, and limited dummy handling. The direct-map path cannot represent partial mappings larger than the per-chip 16 MiB window.

## Test Signals

Tests should exercise normal opcode-only, address-only, read, write, 4-byte address, six-byte RDID, dummy-byte reads, unsupported fast read, unsupported DTR and multi-bit bus widths, and `adjust_op_size` truncation.

Fault tests should verify UMA timeout propagation, host stall/un-stall behavior, absent SHM regmap, direct-map bounds per chip select, memory resource smaller than advertised, and write/erase command behavior through SPI NOR clients. Static analysis should flag the missing unstall after successful `exec_op` and ignored UMA return values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-wpcm-fiu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xcomm.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xcomm.c

## Purpose

`spi-xcomm.c` is an I2C-to-SPI bridge driver for the Analog Devices AD-FMCOMMS1-EBZ board. It registers an SPI controller backed by short I2C commands and also exposes one optional GPIO output through gpiolib.

The bridge supports 16 chip selects, 8-bit words, half-duplex SPI, CPOL/CPHA, 3-wire mode, and a small set of clock dividers derived from a 48 MHz bridge clock.

## Important APIs, Types, and Functions

`struct spi_xcomm` stores the I2C client, optional `gpio_chip`, cached bridge settings, chip-select bitmask, current speed, and a 63-byte command buffer.

GPIO support is provided by `spi_xcomm_gpio_add()`, `spi_xcomm_gpio_set_value()`, and `spi_xcomm_gpio_get_direction()`. Bridge configuration is handled by `spi_xcomm_sync_config()`, `spi_xcomm_chipselect()`, and `spi_xcomm_setup_transfer()`. Data movement is done by `spi_xcomm_txrx_bufs()`.

The SPI controller entry point is `spi_xcomm_transfer_one()`, installed as `transfer_one_message`. Probe allocates a devm SPI host, assigns controller capabilities, registers it, then registers the optional GPIO chip.

## Control Flow

Probe is driven by I2C ID `"spi-xcomm"`. It allocates a SPI host with `struct spi_xcomm` private data, stores the I2C client, advertises 16 chip selects, CPHA/CPOL/3WIRE mode bits, 8-bit words, half-duplex behavior, and registers `spi_xcomm_transfer_one()`.

For a SPI message, the driver sets the selected chip bit in its cached chip-select mask, then iterates each transfer. It rejects transfers with length but neither TX nor RX buffer, rejects transfers longer than 62 bytes, updates clock divider and mode bits in a local settings word, handles `cs_change` relative to whether the transfer is last, and synchronizes bridge configuration when needed.

TX transfers send command `SPI_XCOMM_CMD_WRITE` followed by payload via `i2c_master_send()`. RX transfers first sync configuration with the expected data length, then call `i2c_master_recv()`. Successful transfer byte counts are added to `msg->actual_length`, transfer delays are executed, and chip select is deasserted unless `cs_change` keeps it active.

The GPIO side channel sends `SPI_XCOMM_CMD_GPIO_SET` plus one byte over I2C whenever the GPIO output is changed.

## State and Persistence Behavior

The driver persists only in-memory cached bridge settings, selected chip bits, and current speed. Hardware state in the bridge persists until overwritten by later config or GPIO commands. The driver has no durable storage.

SPI target devices may be modified by write transfers, and the GPIO output state may remain set on the external board. Cached `current_speed` avoids recomputing divider settings unless the requested transfer speed changes.

## Dependencies and Integration Points

The file depends on I2C, SPI controller, gpiolib, unaligned big-endian helpers, and module/I2C driver infrastructure. It integrates with the board bridge firmware through command bytes `UPDATE_CONFIG`, `WRITE`, and `GPIO_SET`.

SPI integration uses `transfer_one_message` rather than `transfer_one`, sets `SPI_CONTROLLER_HALF_DUPLEX`, and finalizes messages through `spi_finalize_current_message()`. GPIO integration is optional and skipped when `CONFIG_GPIOLIB` is disabled.

## Risks and Edge Cases

The bridge buffer is 63 bytes and the SPI payload limit is 62 bytes to reserve one command byte. Larger transfers rely on upper layers splitting messages; otherwise they fail with `-EINVAL`.

The same bit (`BIT(5)`) is used by named setting `SPI_XCOMM_SETTINGS_CS_HIGH` and by the per-transfer `cs_change ^ is_last` handling. This appears intentional for bridge config, but it makes code review easy to confuse because the local variable is not named around CS hold semantics.

Clock divider selection only has divide-by-4, divide-by-16, and divide-by-64 choices. Requests below or above supported rates are rounded coarsely. `current_speed` is updated when speed changes, but if later code clears only the divider bits incorrectly, stale divider state could matter; current code starts from cached settings and sets one divider choice.

The driver supports either TX or RX per transfer, not simultaneous full-duplex. It also does not expose advanced delay, multi-IO, or DMA behavior.

## Test Signals

Tests should cover probe over I2C, SPI device creation, all advertised modes, 3-wire mode, 16 chip-select positions, `cs_change` across multi-transfer messages, 0-byte transfers, 62-byte success and 63-byte rejection, TX and RX short-count I2C errors, GPIO set behavior, and operation with gpiolib disabled.

Integration tests should verify bridge command byte ordering, big-endian config fields, clock divider selection at threshold speeds, and message finalization/status after mid-message I2C failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xcomm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xilinx.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xilinx.c

## Purpose

`spi-xilinx.c` is a host-mode driver for older Xilinx OPB/AXI SPI IP blocks. It uses the Linux `spi_bitbang` framework with custom chip-select, setup, and buffer transfer routines that drive the controller FIFO directly, optionally using the controller's TX-empty interrupt for long transfers.

The driver supports platform data and device-tree configuration, up to 32 chip selects, selectable endian register access, CPOL/CPHA, LSB-first, loopback, and fixed hardware-configured SPI clock.

## Important APIs, Types, and Functions

`struct xilinx_spi` embeds `struct spi_bitbang` first, then stores completion, register base, IRQ, force-IRQ flag, TX/RX pointers, bytes per word, detected FIFO size, inactive chip-select mask, and endian-specific register access functions.

Register definitions cover the SPI control/status/TX/RX/slave-select registers and IPIF global interrupt, interrupt status/enable, and reset registers. Interrupt masks include TX empty and several errors that should not occur in host-only operation.

Endian helpers are `xspi_read32()`, `xspi_write32()`, `xspi_read32_be()`, and `xspi_write32_be()`. Data helpers are `xilinx_spi_tx()` and `xilinx_spi_rx()`. Hardware setup and discovery are `xspi_init_hw()` and `xilinx_spi_find_buffer_size()`.

SPI bitbang hooks are `xilinx_spi_chipselect()`, `xilinx_spi_setup_transfer()`, and `xilinx_spi_txrx_bufs()`. `xilinx_spi_irq()` completes long interrupt-assisted transfers. Probe and remove are `xilinx_spi_probe()` and `xilinx_spi_remove()`.

## Control Flow

Probe reads platform data or device properties for chip-select count, bits per word, and optional forced IRQ mode. It validates chip-select count, allocates a SPI host, initializes bitbang hooks, maps registers, detects register endianness by writing and reading the loopback control bit, sets `bytes_per_word`, detects FIFO size by resetting and writing until TX full, optionally requests an IRQ, initializes hardware, and starts the bitbang controller.

Chip select updates the control register mode bits from the SPI device and writes the slave-select register. The inactive CS mask is updated during setup based on `SPI_CS_HIGH`, and activation toggles the target bit from that inactive mask.

Transfers begin with the transmitter inhibited. The driver sets TX/RX pointers and computes remaining words. If an IRQ exists and either forced or the transfer exceeds FIFO size, it inhibits transmission, clears stale IPIF interrupts, enables global interrupt, and waits on a completion for TX empty. Otherwise it polls status.

For each chunk, it fills the TX FIFO up to detected FIFO capacity, releases inhibit to start transfer, waits for completion or polls status, inhibits again in IRQ mode, then drains RX FIFO for the same number of words. A stall detector resets hardware and fails if TX does not empty and RX remains empty for repeated reads at the start of a chunk.

Remove stops the bitbang controller and disables IPIF interrupts.

## State and Persistence Behavior

The driver stores volatile controller state only: detected endian accessors, FIFO capacity, inactive chip-select mask, transfer pointers, completion state, and IRQ mode. Hardware registers are reset and initialized at probe and after detected stalls.

No file-backed state is used. SPI target devices may persist changes made by transfers. The SPI clock is not programmable by this driver because it is fixed by IP block design parameters.

## Dependencies and Integration Points

The driver depends on platform bus, optional platform data (`struct xspi_platform_data`), device tree compatibles for Xilinx AXI/XPS SPI, MMIO, IRQs, completions, and `spi_bitbang`.

It integrates with legacy board files by instantiating platform-data `spi_board_info` devices after controller start, and with device tree through `xlnx,num-ss-bits` and `xlnx,num-transfer-bits`.

## Risks and Edge Cases

TX/RX word access casts user buffers to `u16 *` or `u32 *` without unaligned helpers, so unaligned buffers on strict-alignment architectures may fault for 16-bit or 32-bit word sizes.

FIFO size detection writes zeros until TX full after reset. If status behavior is unexpected, the detected size can be wrong and later chunking can overrun hardware assumptions.

Interrupt mode waits without a timeout. If TX-empty interrupt is lost, a transfer can hang. Poll mode has a stall detector, but IRQ wait lacks an equivalent timeout.

The driver assumes host-only mode and does not handle mode fault, underrun, or overrun interrupts beyond ignoring them. Hardware or wiring faults may be hard to diagnose.

## Test Signals

Tests should cover little- and big-endian register access, device-tree and platform-data probe, valid and invalid chip-select counts, bits-per-word values 8/16/32 as configured, all mode bits, CS high/low inactive masks, FIFO-size detection, short poll transfers, long IRQ transfers, forced IRQ mode, TX-only/RX-only/full-duplex, and stall recovery.

Static analysis should inspect unaligned access risks and no-timeout IRQ waits. Fault injection should cover missing IRQ, stale IPIF interrupt status, register mapping failure, and `spi_bitbang_start()` failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xilinx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xlp.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xlp.c

## Purpose

`spi-xlp.c` is a platform SPI controller driver for Broadcom/Netlogic XLP-family hardware, matched through ACPI IDs. It registers a four-chip-select SPI host using interrupt-completed FIFO transfers and splits each SPI transfer into hardware-safe chunks of at most 28 bytes.

The driver supports CPOL, CPHA, CS high, per-device speed divisor programming, and basic TX, RX, and full-duplex operation.

## Important APIs, Types, and Functions

`struct xlp_spi_priv` contains MMIO base, current TX/RX pointers and lengths, TX underflow/RX overflow counters, selected chip select, clock rate, command-continuation flag, device copy for logging, and a completion.

Register definitions cover per-chip-select config, frequency divisor, command, status, interrupt enable, FIFO threshold/count, TX/RX FIFOs, and global system control. Important limits are `XLP_SPI_FIFO_SIZE`, `XLP_SPI_MAX_CS`, divisor min/max, and `XLP_SPI_XFER_SIZE` of 28 bytes.

Hardware helpers are `xlp_spi_reg_read()`, `xlp_spi_reg_write()`, `xlp_spi_sysctl_write()`, and `xlp_spi_sysctl_setup()`. SPI setup is `xlp_spi_setup()`, FIFO access is `xlp_spi_fill_txfifo()` and `xlp_spi_read_rxfifo()`, and interrupt handling is `xlp_spi_interrupt()`.

Transfer orchestration uses `xlp_spi_send_cmd()`, `xlp_spi_xfer_block()`, `xlp_spi_txrx_bufs()`, and `xlp_spi_transfer_one()`. Probe maps resources, requests IRQ, reads the SPI clock, allocates/registers the controller, and initializes system control.

## Control Flow

Probe allocates private memory, maps the controller registers, requests the platform IRQ, obtains the SPI clock, allocates a SPI host, assigns four chip selects, setup and transfer callbacks, initializes the completion, attaches private data, resets/enables all SPI channels through `XLP_SPI_SYSCTRL`, and registers the controller.

`xlp_spi_setup()` computes a divisor from controller clock and requested device speed, clamps it to hardware limits, writes FIFO thresholds, and updates config bits for CPHA, CPOL, CS polarity, LSB-first, MOSI/MISO enable, and RX capture for minimum divisor.

`transfer_one()` records the chip select and device, sets `cmd_cont` depending on whether this transfer is the last in the current SPI message, calls `xlp_spi_txrx_bufs()`, finalizes the current transfer, and returns an error if any chunk failed.

`xlp_spi_txrx_bufs()` loops over the transfer length in 28-byte blocks. Each block sets TX/RX pointers and lengths, preloads TX FIFO, writes a command word with TX/RX mode, continuation bit, and bit count, enables RX/TX/done/error interrupts, and waits up to one second for completion. The ISR refills TX FIFO, drains RX FIFO, counts underflow/overflow, clears interrupt status, and completes the wait on transfer-done.

## State and Persistence Behavior

All state is volatile. Per-device persistent hardware programming includes divisor and mode bits in each chip-select register after setup. Per-transfer state lives in private TX/RX pointers, lengths, error counters, selected CS, and completion.

The driver does not store data durably. SPI target devices can persist writes performed through the controller.

## Dependencies and Integration Points

The driver depends on platform devices, ACPI matching (`BRCM900D`, `CAV900D`), clocks, MMIO, IRQs, completions, and SPI controller APIs. It does not use device tree matching in this file.

SPI integration uses controller `setup` and `transfer_one`, `spi_transfer_is_last()` for chip-select continuation, and `spi_finalize_current_transfer()` after synchronous completion.

## Risks and Edge Cases

`struct xlp_spi_priv` contains a full `struct device dev` and `transfer_one()` assigns `xspi->dev = spi->dev`. Copying `struct device` by value is unusual and can be unsafe because devices contain embedded state, locks, and references. Logging should normally use a `struct device *`.

`xlp_spi_txrx_bufs()` returns `bytesleft`, which is zero on success. `transfer_one()` treats any nonzero return as error, so success works, but the helper does not return the transferred byte count like many SPI helpers. Future changes could misinterpret this contract.

The driver waits for completion with a one-second timeout per 28-byte chunk; large transfers can take many seconds if hardware repeatedly times out. Underflow/overflow errors are logged but do not make `xlp_spi_xfer_block()` fail if transfer-done arrived.

FIFO packing/unpacking reverses byte order within each 32-bit FIFO word. This may be hardware-required, but tests must verify byte order for non-multiple-of-four transfers.

## Test Signals

Tests should cover ACPI probe, clock absence, IRQ request failure, divisor clamp at min/max, all supported mode bits, four chip selects, TX-only/RX-only/full-duplex transfers, sizes 1..32 bytes, exact 28-byte split, multi-chunk messages with continuation, timeout handling, underflow/overflow status, and byte ordering for 1/2/3/4-byte chunks.

Static review should flag the by-value `struct device` copy and verify error-counter semantics. Runtime stress should queue multiple transfers to different chip selects and speeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xlp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xtensa-xtfpga.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-xtensa-xtfpga.c

## Purpose

`spi-xtensa-xtfpga.c` is a minimal SPI bitbang driver for the Cadence/Xtensa xtfpga SPI block. The hardware exposes only start, busy, and data registers, and the driver advertises no RX support.

It supports mode 0 word transmission with 1-to-16-bit words, batching outgoing bits into 16-bit hardware writes.

## Important APIs, Types, and Functions

`struct xtfpga_spi` embeds `struct spi_bitbang`, stores MMIO registers, an accumulated data shift register, and the number of valid accumulated bits.

The hardware register interface is `XTFPGA_SPI_START`, `XTFPGA_SPI_BUSY`, and `XTFPGA_SPI_DATA`. `xtfpga_spi_write32()` and `xtfpga_spi_read32()` use raw MMIO accessors. `xtfpga_spi_wait_busy()` polls busy for up to `BUSY_WAIT_US`.

The bitbang TX callback is `xtfpga_spi_txrx_word()`: it appends the outgoing word bits to the accumulator and whenever at least 16 bits are available, writes the top 16 bits to DATA, pulses START, and waits for not-busy. `xtfpga_spi_chipselect()` warns if a transfer ends with unflushed partial bits and resets the accumulator size.

Probe and remove are `xtfpga_spi_probe()` and `xtfpga_spi_remove()`.

## Control Flow

Probe allocates a devm SPI host, advertises `SPI_CONTROLLER_NO_RX`, 1..16 bits per word, and bus id from the platform device. It initializes bitbang hooks for mode 0 only, maps the register resource, clears START, waits briefly, rejects hardware stuck in busy state, starts the bitbang engine, and stores the host as platform data.

During transfers, the SPI bitbang core calls `xtfpga_spi_txrx_word()` for each word. The function appends bits to an accumulator until it has at least 16 bits, then writes one 16-bit frame and toggles START. There is no receive path and no explicit chip-select hardware control in this driver.

Remove stops the bitbang engine and drops the controller reference.

## State and Persistence Behavior

The driver has only volatile accumulator state (`data`, `data_sz`) and MMIO register state. No persistent local storage exists. Transmitted data can modify external SPI devices, but the driver does not track those effects.

Partial accumulated data smaller than 16 bits is not transmitted before chip-select change; `xtfpga_spi_chipselect()` only warns and clears the counter.

## Dependencies and Integration Points

The driver depends on platform devices, optional device tree compatible `"cdns,xtfpga-spi"`, MMIO, delays, and `spi_bitbang`. It also has a platform module alias `xtfpga_spi`.

SPI integration is intentionally narrow: no RX, only mode 0 `txrx_word`, and bit widths up to 16 bits.

## Risks and Edge Cases

Transfers whose total bit count is not a multiple of 16 can lose trailing bits because partial accumulated data is cleared on chipselect with only a warning. This is the most important behavioral risk.

`xtfpga_spi_wait_busy()` emits a warning after 100 microseconds but does not return an error to the SPI core, so hardware stalls can appear as successful transfers. Raw MMIO accessors bypass endianness conversion expectations and are suitable only for the intended platform.

No explicit chip-select register is programmed, so chip-select behavior depends on the bitbang framework or external wiring; tests should confirm target selection on actual xtfpga hardware.

## Test Signals

Tests should cover probe with busy clear and stuck busy, transfer bit widths 1, 8, 16, total bit lengths that are and are not multiples of 16, repeated transfers to verify accumulator reset, remove after bitbang start, and hardware busy timeout behavior.

Static checks should verify that `SPI_CONTROLLER_NO_RX` is honored by clients and that no caller expects readback data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-xtensa-xtfpga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynq-qspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-zynq-qspi.c

## Purpose

`spi-zynq-qspi.c` is a SPI memory controller driver for the Xilinx Zynq QSPI controller. It exposes the controller through `spi-mem` operations, supports up to two chip selects, dual/quad mode bits, per-operation frequency, and interrupt-driven FIFO transfer of command, address, dummy, and data phases.

The driver disables linear mode, uses manual chip select, and performs all SPI memory operations through programmed FIFO writes and RX draining.

## Important APIs, Types, and Functions

`struct zynq_qspi` stores device, MMIO base, reference and APB clocks, IRQ, active TX/RX pointers, remaining byte counters, and a completion.

Register definitions cover QSPI config, status/interrupt registers, enable, delay, TX data registers for 1/2/3/4-byte writes, RX data, thresholds, GPIO, linear config, and module ID. Important masks control manual start/select, baud divisor, FIFO width, master mode, RX/TX interrupt bits, linear two-memory mode, upper page, and FIFO thresholds.

Hardware and SPI MEM helpers include `zynq_qspi_init_hw()`, `zynq_qspi_supports_op()`, `zynq_qspi_chipselect()`, `zynq_qspi_config_op()`, `zynq_qspi_setup_op()`, `zynq_qspi_txfifo_op()`, `zynq_qspi_rxfifo_op()`, `zynq_qspi_write_op()`, `zynq_qspi_read_op()`, `zynq_qspi_irq()`, and `zynq_qspi_exec_mem_op()`.

Probe and remove are `zynq_qspi_probe()` and `zynq_qspi_remove()`.

## Control Flow

Probe allocates a SPI host, maps registers, enables `pclk` and `ref_clk`, initializes the completion, requests IRQ, reads optional `num-cs`, validates the two-CS limit, sets SPI MEM callbacks and per-operation-frequency capability, sets max speed to `refclk / 2`, initializes hardware, and registers the controller.

Hardware initialization disables the controller and interrupts, disables linear mode while enabling two-memory mode if more than one chip select exists, drains RX FIFO, clears status, configures master/manual-CS/flash-interface/FIFO-width bits, sets thresholds, and enables the controller.

`supports_op` accepts SPI MEM operations supported by the default helper and rejects address phases longer than three bytes. `exec_mem_op` asserts chip select, configures mode and baud divisor from the SPI device and operation max frequency, then executes command, address, dummy, and data phases sequentially. Each phase sets TX/RX pointers and byte counts, primes TX FIFO, enables RX/TX interrupts, and waits up to one second for completion. Data-in uses dummy zero TX bytes to clock RX data.

The IRQ handler acknowledges status, drains RX when RX-not-empty is set, writes more TX data when TX-not-full indicates room, disables RX/TX interrupts when both counters reach zero, and completes the phase.

Remove unregisters the controller and disables QSPI.

## State and Persistence Behavior

Driver state is volatile: clock handles, MMIO mapping, active buffers/counters, completion, and controller configuration. The hardware retains mode, baud, chip-select page, threshold, and enable bits until changed or disabled.

SPI memory operations can change attached flash contents for program/erase commands, but the driver itself stores no durable state or cache. Two-chip-select systems use the linear config upper-page bit to select lower or upper memory.

## Dependencies and Integration Points

The driver depends on platform/OF resources, clocks named `"pclk"` and `"ref_clk"`, IRQs, MMIO, completions, and SPI MEM. It matches `"xlnx,zynq-qspi-1.0"`.

Integration with SPI NOR occurs through `spi_controller_mem_ops` and `spi_controller_mem_caps.per_op_freq`. Controller setup refuses changes while the SPI core marks the controller busy.

## Risks and Edge Cases

`zynq_qspi_exec_mem_op()` uses `xqspi->txbuf` as scratch storage for address bytes after the command phase, but `xqspi->txbuf` still points at `op->cmd.opcode`, a one-byte field. Writing `op->addr.nbytes` bytes through it is a strong memory corruption risk. It should use a local address buffer.

If an earlier phase times out and sets `err`, later phases still run because the code does not stop after every timeout. This can leave chip select asserted longer and issue partial operations.

The driver allocates a dummy buffer for dummy cycles and returns `-ENOMEM` without deasserting chip select if allocation fails. Similar early returns should be audited for chip-select cleanup.

Only three-byte addresses are supported, so large flashes requiring four-byte address opcodes must use different command forms or fail. Interrupt waits use fixed one-second timeouts per phase rather than transfer-size-derived timeouts.

## Test Signals

Tests should cover probe with one and two chip selects, missing clocks, invalid `num-cs`, all supported SPI MEM phase combinations, address lengths 0..4, command-only operations, read and write data, dummy cycles, dual/quad mode advertisement, per-operation frequency divisors, timeout per phase, and remove disabling hardware.

Static and fault tests should target the address scratch-buffer bug, chip-select cleanup on allocation failure, phase-timeout short-circuiting, RX/TX counter underflow, and interrupt status handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynq-qspi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynqmp-gqspi.c -->
# sources/distributed-fs/ceph-client/drivers/spi/spi-zynqmp-gqspi.c

## Purpose

`spi-zynqmp-gqspi.c` is the SPI memory controller driver for Xilinx Zynq UltraScale+ MPSoC and Versal GQSPI hardware. It drives generic FIFO command entries, supports single/dual/quad bus widths, up to two chip selects, per-operation frequency changes, RX DMA for aligned larger reads, runtime PM, and platform-specific tap-delay programming.

The driver is host-mode only and exposes the controller through `spi-mem` rather than generic SPI message transfers.

## Important APIs, Types, and Functions

`struct zynqmp_qspi` stores the SPI controller, MMIO base, clocks, IRQ, device, active TX/RX buffers and counters, selected GENFIFO CS/bus bits, RX DMA byte count and mapped address, current GENFIFO entry, IO-vs-DMA mode, completion, operation mutex, current speed, and tap-delay quirk flag. `struct qspi_platform_data` stores match quirks; Versal enables `QSPI_QUIRK_HAS_TAPDELAY`.

Register and mask definitions cover GQSPI config/status/interrupt/enable, TX/RX data, generic FIFO, FIFO control/thresholds, QSPI DMA destination registers, tap-delay registers, mode bits, chip-select/bus select bits, DMA alignment, speed thresholds, and PM timeout.

Core helpers include `zynqmp_gqspi_read()`, `zynqmp_gqspi_write()`, `zynqmp_gqspi_selecttarget()`, `zynqmp_qspi_set_tapdelay()`, `zynqmp_qspi_init_hw()`, `zynqmp_qspi_chipselect()`, `zynqmp_qspi_selectspimode()`, `zynqmp_qspi_config_op()`, `zynqmp_qspi_filltxfifo()`, `zynqmp_qspi_readrxfifo()`, `zynqmp_qspi_fillgenfifo()`, `zynqmp_qspi_setuprxdma()`, `zynqmp_qspi_write_op()`, `zynqmp_qspi_read_op()`, `zynqmp_qspi_irq()`, and `zynqmp_qspi_exec_op()`.

PM hooks are `zynqmp_qspi_suspend()`, `zynqmp_qspi_resume()`, `zynqmp_runtime_suspend()`, and `zynqmp_runtime_resume()`. Probe/remove manage clocks, runtime PM, IRQ, DMA mask, and SPI controller registration.

## Control Flow

Probe allocates a devm SPI host, stores private state as platform data, reads match quirks, maps registers, obtains clocks, enables clocks, initializes completion and operation mutex, enables runtime PM with autosuspend, initializes controller mode/speed, configures GQSPI hardware, requests IRQ, sets a 44-bit DMA mask, validates optional `num-cs`, fills SPI MEM callbacks/capabilities, registers the controller, and puts the device into autosuspend.

Hardware init selects GQSPI mode, clears/disable interrupts and DMA status, disables the controller, programs manual GENFIFO start, little-endian TX FIFO, clock phase/polarity defaults, baud divisor for current speed, tap delays through firmware or local registers, resets FIFOs, sets thresholds, selects lower CS/bus by default, initializes destination DMA control, and enables the controller.

`exec_op` serializes operations with `op_lock`, updates speed/tap delay if needed, asserts chip select through GENFIFO CS setup, builds a base GENFIFO entry from current CS/bus, and executes command, address, dummy, and data phases. Write-like phases fill GENFIFO length entries, preload TX FIFO, start GENFIFO, enable TX/GENFIFO interrupts, and wait for completion using a size-derived timeout. Read data phases choose DMA when the RX buffer is 4-byte aligned and at least eight bytes; otherwise they use IO-mode RX interrupts. DMA completion unmaps the buffer, accounts bytes, disables DMA interrupt, and switches to IO for trailing unaligned bytes.

The IRQ handler clears GQSPI status, reads DMA status in DMA mode, services TX-not-full by filling TX FIFO, handles DMA done through `zynqmp_process_dma_irq()`, drains RX FIFO for IO reads when GENFIFO is empty enough, and completes the phase when TX/RX counters reach zero and the expected interrupt mask is present.

System suspend suspends the SPI controller and disables GQSPI; resume re-enables and resumes. Runtime suspend disables clocks; runtime resume enables clocks.

## State and Persistence Behavior

No file-backed state is used. Persistent hardware state includes current speed divisor, tap-delay configuration, selected CS/bus bits, FIFO thresholds, DMA control, and enable state. Runtime PM can disable clocks between operations; operation state is re-established through setup/init paths.

Per-operation state is kept in buffer pointers, byte counters, GENFIFO entry, DMA address, DMA byte count, and mode. External SPI flash contents may be persistently changed by program/erase operations sent through `spi-mem`.

## Dependencies and Integration Points

The driver depends on platform/OF matching (`"xlnx,zynqmp-qspi-1.0"` and `"xlnx,versal-qspi-1.0"`), clocks, MMIO, IRQs, DMA mapping, firmware API `zynqmp_pm_set_tapdelay_bypass()`, runtime PM, completions, mutexes, and SPI MEM.

SPI integration uses `mem_ops.exec_op`, `mem_caps.per_op_freq`, `setup`, automatic runtime PM, mode bits for CPOL/CPHA and dual/quad TX/RX, and 8-bit words. DMA integration is register-level destination DMA rather than DMAengine.

## Risks and Edge Cases

`zynqmp_qspi_filltxfifo()` appears to update `count` after setting `bytes_to_transfer = 0` in the short trailing-byte branch, so `count += xqspi->bytes_to_transfer` adds zero. The loop still exits because bytes become zero, but accounting is confusing and should be reviewed.

The command phase stores a 16-bit `opcode` and transmits `op->cmd.nbytes`; most SPI MEM commands are one byte, but multi-byte command assumptions should be tested for byte order. Address bytes are staged in a local `u64 opaddr`, which avoids the Zynq driver's scratch-buffer problem.

Completion requires both byte counters to reach zero and a specific interrupt-mask pattern. Unexpected hardware status ordering can cause timeouts even after data movement. RX DMA is used only for aligned reads and leaves remainder bytes for IO mode; transition correctness is important.

Tap-delay programming differs between ZynqMP firmware calls and Versal local registers. Errors from firmware tap-delay calls are ignored, so bad firmware responses may silently degrade high-speed timing.

Runtime PM error paths are complex: probe calls `pm_runtime_get_sync()` and multiple error labels disable PM/clocks. Remove calls `pm_runtime_get_sync()` without checking its return. These paths need fault-injection coverage.

## Test Signals

Tests should cover ZynqMP and Versal compatibles, tap-delay branches at 37.5/40/100/150 MHz thresholds, one and two chip selects, lower/upper bus selection, command/address/dummy/data phase combinations, single/dual/quad bus widths, per-operation speed changes, TX writes, RX IO reads, aligned RX DMA reads, unaligned and short RX reads, DMA remainder transition, timeouts, runtime autosuspend/resume, system suspend/resume, invalid `num-cs`, DMA mask failure, and IRQ ordering.

Static analysis should inspect TX FIFO trailing-byte accounting, ignored tap-delay firmware return values, runtime PM unwind paths, and completion conditions in the IRQ handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/spi/spi-zynqmp-gqspi.c -->
