# sources/distributed-fs/ceph-client/drivers/spi/spi-cadence.c

## Purpose

`spi-cadence.c` is the basic Cadence SPI controller driver for host and target mode controllers such as Xilinx Zynq and compatible `cdns,spi-r1p6` variants. It implements FIFO-driven SPI transfers with interrupt completion, manual chip-select handling in host mode, target abort support, FIFO depth detection, optional reset control, and runtime PM for host mode.

## Important APIs, Types, and Functions

`struct cdns_spi` stores MMIO registers, APB/reference clocks, cached clock rate, current speed, TX/RX buffer pointers and remaining word counts, bytes-per-word, decoded-CS state, detected FIFO depth, and reset control. Main functions are `cdns_spi_init_hw()`, `cdns_spi_chipselect()`, `cdns_spi_config_clock_mode()`, `cdns_spi_config_clock_freq()`, `cdns_spi_process_fifo()`, `cdns_spi_irq()`, `cdns_transfer_one()`, `cdns_prepare_transfer_hardware()`, `cdns_unprepare_transfer_hardware()`, `cdns_target_abort()`, `cdns_spi_probe()`, and PM callbacks.

## Control Flow

Probe chooses `spi_alloc_target()` when the `spi-slave` property is present, otherwise `spi_alloc_host()`. It maps registers, enables `pclk` and `ref_clk`, toggles optional reset, sets up runtime PM and chip-select properties for host mode, detects FIFO depth by writing the threshold register, initializes hardware, requests the IRQ, fills controller callbacks and mode bits, and registers the controller.

For each host transfer, `cdns_transfer_one()` configures clock frequency, sets current TX/RX buffers and counts, converts byte length to word count based on `bits_per_word`, preloads the FIFO, enables TX-overwater and mode-fault interrupts, and returns a positive length so the SPI core waits. The IRQ handler acknowledges status, handles mode fault by disabling interrupts and finalizing, or handles TX-overwater by draining received words, filling more TX words, lowering the threshold near the end, and finalizing after the final drain. Target mode uses the same FIFO helpers but skips clock and CS setup; `target_abort` disables relevant interrupts and finalizes.

## State and Persistence Behavior

State is volatile and per-controller. The cached `speed_hz`, `current` buffers, word counters, FIFO threshold, decoded-CS mode, and current enable state survive between transfers until reconfigured. Runtime PM disables/enables both clocks for host mode; system resume reinitializes controller registers. There is no persistent storage, but SPI transfers can change attached devices.

## Dependencies and Integration Points

The driver depends on platform/OF probing, clocks, reset controls, IRQs, runtime PM, GPIO-descriptor chip-select integration, and the SPI core. OF properties include `spi-slave`, `num-cs`, and `is-decoded-cs`. The `cix,sky1-spi-r1p6` compatible expands allowed `bits_per_word` to 16 and 32, while default compatibles are 8-bit only.

## Risks and Edge Cases

The reader/writer functions only log and return on unaligned buffers, but the transfer continues with unchanged counters already decremented by `cdns_spi_process_fifo()`, which can produce data loss rather than an error. The IRQ path uses a fixed 10 us delay to work around unreliable RX-not-empty status. Runtime PM is configured only for host mode, so target-mode clock lifetime relies on devm-enabled clocks. Clock divisor selection silently chooses the nearest lower speed. Transfer completion on mode fault depends on the SPI core noticing nonzero remaining bytes.

## Test Signals

Tests should cover probe in host and target mode, decoded and nondecoded CS, 8/16/32-bit modes for the CIX compatible, unaligned buffer fault behavior, FIFO depth detection, long transfers crossing FIFO thresholds, RX-only/TX-only transfers, mode-fault IRQ, target abort, runtime autosuspend/resume, system suspend/resume, and error paths for missing clocks, reset, IRQ, or MMIO resources.
