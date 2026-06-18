<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/io.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/io.c

## Purpose
Sets up the static OMAP1 IO mappings and exposes legacy physical-address read/write helpers used by older mach-omap1 code.

## Important APIs, Types, and Functions
Defines `omap1_map_io()`, `omap1_init_early()`, `omap1_init_late()`, and exported `omap_readb/w/l()` plus `omap_writeb/w/l()` helpers.

## Control Flow
`omap1_map_io()` installs common IO, DSP, and DSP register mappings. `omap1_init_early()` calls `omap_check_revision()` and clears TIPB bridge control registers for an OMAP5910 erratum. `omap1_init_late()` initializes serial wake support. Accessor helpers translate physical addresses through `OMAP1_IO_ADDRESS()` and issue raw MMIO operations.

## State and Persistence Behavior
Static mappings persist for the life of the kernel. Early init writes TIPB bridge state once; late init may set up serial wake IRQs through `serial.c`.

## Dependencies and Integration Points
Uses ARM `iotable_init()`, `map_desc`, `OMAP1_IO_ADDRESS`, DSP mapping constants, `tc.h`, and common revision/serial wake helpers.

## Risks
The exported raw physical-address helpers bypass ioremap lifetime tracking and ordering semantics. Bad addresses can fault or touch unintended registers. The TIPB workaround is early and unconditional for OMAP1, so address definitions must match actual silicon.

## Test Signals
Boot smoke tests should verify early printk/serial still work, no mapping faults occur, and `/proc/iomem` or debug traces show expected device mappings. Static checks should ensure no new drivers depend on these legacy helpers when normal `ioremap()` is possible.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/io.c -->
