# sources/distributed-fs/ceph-client/drivers/spi/spi-orion.c

Purpose: Marvell Orion/Armada SPI controller driver. It supports 8- and 16-bit PIO transfers, optional direct mapped TX window for suitable writes, runtime PM, GPIO chip selects, LSB-first mode, and SoC-specific clock divisor/erratum behavior.

Important APIs, types, and functions: `struct orion_spi_dev` describes SoC type, max/min divisors, prescale mask, max Hz, and 50 MHz erratum flag. `struct orion_spi` stores host, MMIO base, clocks, devdata, device, and per-CS direct access mapping. Key functions are `orion_spi_baudrate_set()`, `orion_spi_mode_set()`, `orion_spi_50mhz_ac_timing_erratum()`, `orion_spi_setup_transfer()`, `orion_spi_set_cs()`, 8/16-bit write-read helpers, `orion_spi_write_read()`, `orion_spi_transfer_one()`, probe/remove, reset, and runtime PM callbacks.

Control flow: probe allocates a host, resolves bus number, applies match data, enables clocks, calculates max/min speed, maps controller registers, scans child nodes for direct-access address windows, enables runtime PM, resets the controller, and registers. Each transfer programs mode, bitrate, erratum timing, and 8/16-bit mode, then either writes through a direct mapped CS window for 8-bit TX-only non-`SPI_CS_WORD` transfers or loops word-by-word through data out/in registers, clearing interrupt cause and polling ready each word.

State and persistence: hardware configuration is in IF control/config/timing registers. Per-CS direct access virtual address/size is cached at probe. Runtime suspend disables clocks; resume re-enables them. Remove unregisters controller and tears down runtime PM/clocks.

Dependencies and integration points: uses platform resources, OF match data and child address resources, optional AXI clock, runtime PM autosuspend, GPIO descriptors, SPI core transfer_one, unaligned helpers for 16-bit words, and device tree compatibles for several Marvell SoCs.

Risks: ready polling is microsecond-loop based and returns partial byte count on timeout. `SPI_CS_WORD` is only valid for 8-bit words. Direct mapped writes only map one page and only handle TX writes; future NOR/NAND direct support would need broader semantics. Clock divisor logic differs by SoC and old Armada 370 DT compatibility. AXI clock error handling must tolerate optional absence.

Test signals: mode 0..3 and LSB-first, 8/16-bit TX/RX/full-duplex, `SPI_CS_WORD`, direct-access child mapping and fallback, timeout handling, Armada 380 50 MHz CPOL/CPHA erratum, GPIO CS, runtime PM autosuspend, and old/new compatible max-speed calculations.
