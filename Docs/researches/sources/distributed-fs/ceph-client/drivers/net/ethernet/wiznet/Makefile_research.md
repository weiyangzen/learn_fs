# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Makefile

Purpose: maps WIZnet Kconfig symbols to driver objects.

Important build rules: `CONFIG_WIZNET_W5100` builds `w5100.o`, `CONFIG_WIZNET_W5100_SPI` builds `w5100-spi.o`, and `CONFIG_WIZNET_W5300` builds `w5300.o`.

Control flow and integration: `w5100-spi.o` depends on exported symbols from `w5100.o`, so the Kconfig dependency on `WIZNET_W5100` is important. `w5300.o` is independent and implements its own platform driver.

State and persistence: no runtime state.

Risks and tests: incorrect Kconfig dependencies could produce unresolved symbols for SPI support. Build tests should verify module and built-in configurations for each object and combined W5100 plus W5100-SPI builds.
