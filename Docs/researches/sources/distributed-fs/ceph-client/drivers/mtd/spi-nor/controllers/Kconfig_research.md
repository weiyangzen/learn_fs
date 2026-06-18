# sources/distributed-fs/ceph-client/drivers/mtd/spi-nor/controllers/Kconfig

Purpose: Kconfig entries for SPI NOR memory controllers in this subset.

Important APIs/types/functions: `SPI_HISI_SFC` enables the HiSilicon FMC SPI NOR controller for `ARCH_HISI` or compile testing with I/O memory. `SPI_NXP_SPIFI` enables the NXP LPC SPIFI controller for OF and `ARCH_LPC18XX` or compile testing.

Control flow and state: build-time only; selected symbols control inclusion of `hisi-sfc.o` and `nxp-spifi.o`.

Dependencies and integration: sourced by the parent SPI NOR Kconfig and tied to the controllers Makefile. Risks include insufficient dependency coverage for clocks/platform resources and hidden compile-test warnings. Test signals include native and `COMPILE_TEST` builds, OF-disabled builds for SPIFI, and symbol-to-object mapping.
