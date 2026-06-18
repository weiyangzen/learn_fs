# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Makefile

Purpose: build mapping for SPI NOR controller drivers.

Important APIs/types/functions: maps `CONFIG_SPI_HISI_SFC` to `hisi-sfc.o` and `CONFIG_SPI_NXP_SPIFI` to `nxp-spifi.o`.

Control flow and state: build-time only. It has no runtime state.

Dependencies and integration: depends directly on controller Kconfig symbols and parent SPI NOR Makefile recursion. Risks are limited to stale symbol/object names. Test signals are config builds with each controller enabled singly and together.
