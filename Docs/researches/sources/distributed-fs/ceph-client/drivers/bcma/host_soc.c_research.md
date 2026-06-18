# sources/distributed-fs/ceph-client/drivers/bcma/host_soc.c

Purpose: provides BCMA host operations for memory-mapped Broadcom SoC buses. It supports early built-in SoC registration and Open Firmware platform-driver registration, mapping core and wrapper MMIO directly rather than using PCI windows.

Important APIs and functions: `bcma_host_soc_read/write{8,16,32}` directly access `core->io_addr`. Optional block I/O helpers perform raw repeated reads/writes for configured widths. `bcma_host_soc_aread32()` and `_awrite32()` access wrapper/agent registers through `core->io_wrap` and warn if absent. `bcma_host_soc_register()` maps the first core at `BCMA_ADDR_BASE` for early scan setup. `bcma_host_soc_init()` runs `bcma_bus_early_register()`. OF-enabled `bcma_host_soc_probe()` maps the platform resource, initializes the bus, and calls `bcma_bus_register()`.

Control flow: legacy early SoC registration first maps only one core because scanning discovers the rest. Later early init scans and initializes core infrastructure. The OF path allocates a bus with devm memory, maps the first resource from the device tree, initializes and registers the full bus, then stores platform drvdata. Remove unregisters the bus and unmaps MMIO.

State and persistence: `bus->mmio`, `bus->hosttype = BCMA_HOSTTYPE_SOC`, `bus->ops`, `bus->dev`, and per-core `io_addr/io_wrap` mappings are the primary state. Hardware register writes are direct SoC MMIO effects; no separate persistent storage is maintained.

Dependencies and integration points: depends on `scan.h` for base addresses, Linux OF address APIs, platform driver registration, BCMA bus scan/register from `main.c`, and per-core ioremap setup in `scan.c`. It supplies the `bcma_host_ops` used by all core drivers on SoC-hosted BCMA.

Risks: early registration maps a fixed physical base and only the first core, so platform assumptions are strict. Raw block I/O bypasses endian conversion beyond explicit little-endian pointer types. Wrapper accesses can return all ones when no wrapper exists. Test signals include OF compatible `brcm,bus-axi` probe, early SoC boot path, core wrapper access warnings, and correct IRQ/DMA configuration from device tree.
