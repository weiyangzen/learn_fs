# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5624r_spi.c

## Purpose
`ad5624r_spi.c` is an IIO SPI DAC driver for four-channel AD5624R, AD5644R, and AD5664R variants. It exposes raw writes, scale reads, per-channel powerdown, and shared powerdown-mode selection.

## Important APIs, Types, And Functions
- `ad5624r_spi_write()` encodes the 24-bit command frame with command, DAC address, and bit-width-dependent data shift.
- `ad5624r_read_raw()` reports scale from `st->vref_mv` and channel realbits.
- `ad5624r_write_raw()` validates raw DAC codes and writes with `WRITE_INPUT_N_UPDATE_N`.
- Powerdown helpers implement `powerdown` and `powerdown_mode` ext_info attributes.
- Channel macros create 12-, 14-, and 16-bit four-channel tables.
- `ad5624r_probe()` resolves external or internal reference, programs internal reference setup, and registers the IIO device.

## Control Flow
Probe allocates the IIO device, attempts external `vref` then legacy `vcc`, chooses the reference source, selects chip info by SPI ID, assigns channels, writes the internal-reference setup command, and registers. Runtime writes issue one 24-bit SPI frame per raw value. Powerdown writes update the mask and issue a powerdown command carrying mode plus channel mask.

## State And Persistence
The driver stores reference voltage, selected chip info, and powerdown mask/mode. DAC output values persist in hardware but are not cached/read back. Regulators are devm-enabled through helper APIs.

## Dependencies And Integration Points
The file integrates with SPI, regulator consumers, IIO direct mode, IIO sysfs ext_info, and the local `ad5624r.h` definitions. SPI IDs distinguish bit depth and internal reference voltage.

## Risks And Edge Cases
- `ad5624r_probe()` computes `st->vref_mv = external_vref ? ... : st->chip_info->int_vref_mv` before assigning `st->chip_info`; the no-external-reference path can dereference an uninitialized pointer. This is a high-value bug signal.
- The internal-reference setup writes `external_vref` as the payload; the polarity must be checked against the datasheet because the command name suggests enabling internal reference.
- There is no lock or DMA-aligned persistent transfer buffer for the 3-byte stack message, though `spi_write()` copies synchronously for common controllers.
- Raw reads are unsupported; users only get scale and write-only DAC behavior.

## Test Signals
Probe tests must cover external vref, legacy vcc, and no-regulator internal-reference paths. Additional tests should cover command packing for 12/14/16-bit variants, raw bounds, powerdown mask/mode writes, and channel table selection by ID.
