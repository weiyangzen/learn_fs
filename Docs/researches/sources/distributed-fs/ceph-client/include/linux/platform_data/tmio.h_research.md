# sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h

## Purpose
`tmio.h` is a Linux kernel legacy board/platform-data header. It gives board files, MFD children,
ACPI glue, or platform-device setup code a compact contract for passing the primary type `struct
tmio_mmc_data` into the matching driver at probe time.

## Important APIs, types, and functions
Macros/constants: `MFD_TMIO_H`, `TMIO_MMC_BLKSZ_2BYTES`, `TMIO_MMC_SDIO_IRQ`, `TMIO_MMC_MIN_RCAR2`,
`TMIO_MMC_HAS_IDLE_WAIT`, `TMIO_MMC_USE_BUSY_TIMEOUT`, `TMIO_MMC_HAVE_CMD12_CTRL`,
`TMIO_MMC_SDIO_STATUS_SETBITS`, `TMIO_MMC_32BIT_DATA_PORT`, `TMIO_MMC_CLK_ACTUAL`,
`TMIO_MMC_HAVE_CBSY`, `TMIO_MMC_64BIT_DATA_PORT`. Types: `struct tmio_mmc_data`. Declared or inline
functions: none visible in this header. Important struct details: struct tmio_mmc_data fields
include `void *chan_priv_tx`, `void *chan_priv_rx`, `unsigned int hclk`, `unsigned long
capabilities`, `unsigned long capabilities2`, `unsigned long flags`, `u32 ocr_mask`, `dma_addr_t
dma_rx_offset`.

## Control flow
Setup code fills the declared platform-data structure, constants, or callbacks before registering
the platform or auxiliary device. The matching driver reads these values during probe to select
hardware revisions, pins, bus widths, GPIOs, DMA settings, regulator defaults, firmware names, or
callback hooks; later runtime paths use saved copies for interrupt handling, PM, hotplug, media
routing, or register programming. Consumers include `sources/distributed-fs/ceph-
client/drivers/mmc/host/tmio_mmc_core.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_internal_dmac.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/uniphier-sd.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_core.c`.

## State and persistence
The header is declarative and has no persistence by itself. State appears when board code
instantiates the declared structs or constants, when drivers cache the values in their private data,
and when callbacks mutate underlying hardware registers. Values are usually fixed for the lifetime
of the registered device.

## Dependencies and integration points
It includes `linux/platform_device.h`, `linux/types.h`. Direct source-tree consumers found by
include search are `sources/distributed-fs/ceph-client/drivers/mmc/host/tmio_mmc_core.c`,
`sources/distributed-fs/ceph-client/drivers/mmc/host/renesas_sdhi_internal_dmac.c`,
`sources/distributed-fs/ceph-client/drivers/mmc/host/uniphier-sd.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_core.c`, `sources/distributed-fs/ceph-
client/drivers/mmc/host/renesas_sdhi_sys_dmac.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ap325rxa/setup.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-kfr2r09/setup.c`, `sources/distributed-fs/ceph-
client/arch/sh/boards/mach-ecovec24/setup.c`. It integrates through `struct platform_device`
platform data, board files, MFD child registration, and legacy non-DT setup paths; many modern
systems may replace parts of this contract with Device Tree, ACPI, or software-node properties.

## Risks and test signals
Risks are mostly contract drift between platform setup and the consuming driver: wrong enum value,
missing callback, invalid GPIO/IRQ/resource, incompatible register-width or bus-mode flag, or
lifetime bugs when platform data points at temporary storage. Test signals include compile coverage
for the owning architecture, probe with representative board data, DT/ACPI fallback comparison where
available, suspend/resume if callbacks are present, and fault injection for missing optional
resources.

## Source-read signal
Read `sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h` completely for this pass (65 lines, 1860 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/linux/platform_data/tmio.h_research.md`.
