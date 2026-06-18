# sources/distributed-fs/ceph-client/drivers/fpga/ice40-spi.c

Purpose: FPGA manager driver for configuring Lattice iCE40 SRAM over slave SPI. It controls CRESET_B and observes CDONE GPIO while using the SPI bus to stream the bitstream and activation clocks.

Important APIs and functions: `struct ice40_fpga_priv` holds the SPI device and `reset`/`cdone` GPIO descriptors. `ice40_fpga_ops_state` reports operating when CDONE is asserted. `ice40_fpga_ops_write_init` rejects partial reconfiguration, locks the SPI bus, asserts reset and chip select long enough for reset timing, releases reset, verifies CDONE deasserted, performs housekeeping delay, and unlocks. `ice40_fpga_ops_write` calls `spi_write`, and `ice40_fpga_ops_write_complete` requires CDONE asserted then sends zero padding bytes for activation.

Control flow: probe validates SPI max/min speed and CPHA, obtains required GPIOs, and registers a devm FPGA manager. The manager framework calls write-init, write, and write-complete during image load. There is no explicit remove beyond devm cleanup.

State and persistence: Linux state is the SPI device pointer and two GPIO descriptors. Hardware state is volatile SRAM configuration, reset line, CDONE pin, and SPI bus transactions. No bitstream metadata is parsed and no settings persist across power loss.

Dependencies and integration points: depends on SPI core, gpiod consumer API, FPGA manager framework, OF compatible `lattice,ice40-fpga-mgr`, and SPI device ID `ice40-fpga-mgr`.

Risks and test signals: risks include board-specific GPIO polarity requirements, SPI speed/mode misconfiguration, failure to deassert CDONE during reset, CDONE asserted before activation padding is sent, and no support for partial reconfiguration. Test signals are manager registration, successful state transition to operating, expected reset/CDONE timing on a logic analyzer, SPI transfer success, and failure returns when CDONE remains low after transfer.
