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
