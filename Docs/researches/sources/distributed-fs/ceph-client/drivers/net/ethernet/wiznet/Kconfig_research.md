# sources/distributed-fs/ceph-client/drivers/net/ethernet/wiznet/Kconfig

Purpose: Kconfig menu for WIZnet Ethernet drivers.

Important options: `NET_VENDOR_WIZNET` gates the vendor menu and depends on `HAS_IOMEM`. `WIZNET_W5100` enables the W5100 core/platform driver. `WIZNET_W5300` enables the W5300 platform driver. The `WIZNET_BUS_DIRECT`, `WIZNET_BUS_INDIRECT`, and `WIZNET_BUS_ANY` choice controls whether MMIO direct, MMIO indirect, or runtime-selected access code is built. `WIZNET_W5100_SPI` enables SPI support for W5100/W5200/W5500 and depends on `WIZNET_BUS_ANY`, `WIZNET_W5100`, and `SPI`.

Integration: Makefile objects depend directly on these symbols. The bus-mode choice affects compiled function selection and therefore performance, locking, and whether SPI can be selected.

State and persistence: no runtime state, but selected options alter the code paths compiled into `w5100.o`, `w5100-spi.o`, and `w5300.o`.

Risks and tests: `WIZNET_W5100_SPI` is only available with `WIZNET_BUS_ANY`, so static direct/indirect configurations intentionally exclude SPI. Build matrix tests should cover W5100 MMIO direct, indirect, any, SPI, and W5300 combinations.
