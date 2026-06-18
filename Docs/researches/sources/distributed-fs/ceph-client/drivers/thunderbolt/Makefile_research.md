# sources/distributed-fs/ceph-client/drivers/thunderbolt/Makefile

## Purpose
The Thunderbolt Makefile composes the main `thunderbolt` driver object and optional ACPI, debugfs, KUnit, and DMA test objects.

## Important APIs, Types, and Functions
`obj-${CONFIG_USB4}` builds `thunderbolt.o`. Core objects include NHI, control, switch, capability, path, tunnel, domain, DMA port, ICM, property, xdomain, link-controller, TMU, USB4, NVM, retimer, quirks, and CLx code. Optional objects include `acpi.o`, `debugfs.o`, `test.o`, and `dma_test.o`.

## Control Flow
Build composition is driven by Kconfig. `ccflags-y := -I$(src)` supports local header inclusion, and `CFLAGS_test.o` disables structleak for KUnit tests.

## State and Persistence Behavior
No runtime state. The selected object list determines module contents.

## Dependencies and Integration Points
It is coupled to `drivers/thunderbolt/Kconfig` and the source files' conditional declarations.

## Risks and Edge Cases
Using `${CONFIG_USB4}` instead of the more common `$(CONFIG_USB4)` is accepted by kbuild but should remain consistent with local style. Optional objects must align with function references guarded by config.

## Test Signals
Build with ACPI on/off, DEBUG_FS on/off, USB4 KUnit, and DMA test module enabled/disabled.
