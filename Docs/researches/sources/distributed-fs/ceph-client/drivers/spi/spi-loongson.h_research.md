# sources/distributed-fs/ceph-client/drivers/spi/spi-loongson.h

## Purpose

`spi-loongson.h` defines the private contract between the Loongson SPI core and its PCI/platform frontends. It names controller registers, bit definitions, shared runtime state, and exported core entry points.

## Important APIs, Types, And Functions

Register offsets include SPCR, SPSR, FIFO, SPER, PARA, SFCS, and TIMI. Important bits include `LOONGSON_SPI_PARA_MEM_EN`, CPHA/CPOL/SPE in SPCR, and RFEMPTY/WCOL/SPIF in SPSR. `struct loongson_spi` stores the SPI controller, MMIO base, cached speed/mode/register values, and clock rate. Public declarations are `loongson_spi_init_controller()` and `loongson_spi_dev_pm_ops`.

## Control Flow, State, And Persistence

The header has no runtime flow. Its structure fields define the volatile state saved across suspend/resume and the cached mode/speed data used by the core transfer path.

## Dependencies And Integration Points

It includes Linux bits, PM, and type headers, and forward-declares `struct device` and `struct spi_controller`. Both Loongson frontend drivers include it and rely on the exported namespace from the core.

## Risks And Test Signals

Risks are ABI drift within the Loongson mini-driver set: register offsets or cached fields must remain consistent with core suspend/resume and transfer code. Compile all three Loongson files together and test probe through both PCI and platform frontends.
