# sources/distributed-fs/ceph-client/drivers/fpga/lattice-sysconfig-spi.c

Purpose: SPI transport adapter for the generic Lattice sysCONFIG FPGA manager core. It supplies command-transfer and bitstream-burst callbacks, enforces ECP5 SPI speed limits, and delegates common programming behavior to `sysconfig_probe`.

Important APIs and functions: `sysconfig_spi_cmd_transfer` implements command reads/writes with `spi_write_then_read`. `sysconfig_spi_bitstream_burst_init` sends `SYSCONFIG_LSC_BITSTREAM_BURST`, locks the SPI bus, and keeps chip select asserted for the burst. `sysconfig_spi_bitstream_burst_write` streams locked transfers with `cs_change`. `sysconfig_spi_bitstream_burst_complete` unlocks the bus and toggles chip select using a zero-length `spi_write`. `sysconfig_spi_probe` fills `struct sysconfig_priv` callbacks and calls `sysconfig_probe`.

Control flow: probe allocates private data, gets the max speed from OF match data or SPI ID data, rejects over-speed devices, attaches transport callbacks, and registers the common manager. During programming, the common core enters ISC mode and calls the SPI burst callbacks to hold bus ownership until bitstream completion.

State and persistence: this file owns no persistent hardware state beyond SPI bus locking during a burst. Its private data is devm-managed and embedded in the common sysCONFIG manager state. Hardware programming persistence depends on the target Lattice device.

Dependencies and integration points: depends on SPI core, OF match data, `lattice-sysconfig.h`, and the exported `sysconfig_probe` from `lattice-sysconfig.c`. It matches `lattice,sysconfig-ecp5` and SPI ID `sysconfig-ecp5`.

Risks and test signals: risks include bus lock leaks if burst init succeeds but common completion is not called, max-speed driver-data casts, and controller behavior for zero-length CS toggles. Test signals are successful manager registration, rejected too-fast SPI settings, correct CS hold across burst writes, sysCONFIG status polling in the common core, and no SPI bus lock after failed writes.
