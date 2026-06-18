# sources/distributed-fs/ceph-client/drivers/spi/spi-hisi-kunpeng.c

## Purpose

`spi-hisi-kunpeng.c` is the HiSilicon Kunpeng SPI host controller driver. It is an interrupt-driven FIFO controller derived conceptually from DesignWare SPI code, supporting configurable clock dividers, 4 to 32 bits per word, loopback, CPOL/CPHA, CS-high, debugfs register visibility, ACPI probing, and per-device cached control register state.

## Important APIs, Types, and Functions

`struct hisi_spi` contains device/MMIO/IRQ/FIFO state plus current transfer pointers and byte width. `struct hisi_chip_data` is per-SPI-device cached state for CR mode bits and calculated divider fields. Core helpers include `hisi_calc_effective_speed()`, `__hisi_calc_div_reg()`, `hisi_spi_prepare_cr()`, `hisi_spi_reader()`, `hisi_spi_writer()`, `hisi_spi_flush_fifo()`, and `hisi_spi_disable()`. SPI callbacks are `hisi_spi_setup()`, `hisi_spi_cleanup()`, `hisi_spi_transfer_one()`, `hisi_spi_handle_err()`, and ISR `hisi_spi_irq()`.

## Control Flow

Probe allocates a host, maps registers, reads `spi-max-frequency` and optional `num-cs`, sets controller capability masks, initializes FIFO thresholds and interrupt masks, requests IRQ, registers the controller, and creates a debugfs register set. Setup allocates per-device chip data and caches loopback, CPOL, and CPHA bits. Each transfer recalculates effective speed and divider fields, writes the CR including bits per word, flushes stale RX data, sets current TX/RX pointers and word counts, enables interrupts and the controller, and returns positive for asynchronous completion.

The ISR checks masked interrupt status, handles RX overflow as `-EIO`, drains RX every interrupt, finalizes when expected RX words are consumed, and writes more TX data when TX IRQ fires. Finalization disables controller/interrupts and calls `spi_finalize_current_transfer()`.

## State and Persistence Behavior

Per-device `hisi_chip_data` persists between setups until cleanup, caching mode bits and the last effective speed. `hisi_spi` transfer pointers are volatile active-transfer state. Hardware FIFOs and registers are reset/disabled between transfers and on error. There is no storage persistence; writes affect attached devices only.

## Dependencies and Integration Points

The driver depends on ACPI match `HISI03E1`, platform MMIO/IRQ resources, debugfs, the SPI core, and firmware properties for max frequency and chip-select count. It uses bitfield helpers for register composition and standard SPI GPIO descriptor support for CS lines.

## Risks and Edge Cases

`hisi_spi_transfer_one()` derives transfer word count as `transfer->len / n_bytes`, so unaligned lengths relative to bits-per-word would silently ignore trailing bytes; the SPI core should constrain such transfers, but tests should cover them. Error handling sleeps 10 ms after disabling to let an in-flight ISR finish rather than using stronger synchronization. The divider calculation forces even dividers and clamps to hardware limits, so actual speed can be lower than requested. Debugfs creation failure is nonfatal.

## Test Signals

Test ACPI probe, missing/zero `spi-max-frequency`, optional `num-cs`, all supported bits-per-word classes, loopback/CPOL/CPHA/CS-high, TX-only/RX-only/full-duplex, RX overflow IRQ injection, timeout/error path, divider edge speeds near min/max, cleanup of per-device chip data, and debugfs register visibility.
