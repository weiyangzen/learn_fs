# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tlc4541.c

Purpose: SPI IIO driver for TI TLC3541/TLC4541 single-channel ADCs, supporting 14-bit and 16-bit variants in direct and triggered-buffer modes.

Important APIs/types/functions: `struct tlc4541_state` stores SPI, vref regulator, a fixed three-transfer SPI message, and aligned receive buffer. `struct tlc4541_chip_info` selects the channel layout. `tlc4541_trigger_handler()` runs the prepared SPI message and pushes timestamped data. `tlc4541_read_raw()` handles direct raw reads and scale. `tlc4541_probe()` sets up variant data, reset write, SPI message, regulator, buffer, and IIO registration.

Control flow: probe chooses TLC3541 or TLC4541 by SPI id, writes a reset/init byte, prepares a transfer sequence matching the device requirement for 24 clocks, conversion delay, and data readback, enables vref, sets up a triggered buffer, and registers IIO. Direct reads claim IIO direct mode, run the same SPI message, decode the big-endian sample by variant shift/realbits, and release direct mode.

State and persistence: no cached device settings except the prepared SPI message and regulator state. Samples are transient in `rx_buf`. Remove unregisters IIO, cleans up the buffer, and disables vref.

Dependencies and integration: SPI, regulator, IIO triggered buffer, OF/SPI IDs `ti,tlc3541` and `ti,tlc4541`.

Risks: probe ignores errors from the initial reset `spi_write`; the delay in the middle transfer is expressed as 3 nanoseconds although comments describe a 2.94 microsecond conversion period, so timing should be checked against SPI core semantics and hardware behavior. Test signals include raw decode for both bit widths, direct/buffer mutual exclusion, scale from vref, and failure cleanup paths.
