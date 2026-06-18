# sources/distributed-fs/ceph-client/drivers/staging/media/av7110/Makefile

## Purpose
Describes object composition and include paths for the AV7110 DVB driver build.

## Important APIs, Types, and Functions
`dvb-ttpci-objs` links `av7110_hw.o`, `av7110_v4l.o`, `av7110_av.o`, `av7110_ca.o`, `av7110.o`, `av7110_ipack.o`, and `dvb_filter.o`, with optional `av7110_ir.o`. `obj-$(CONFIG_DVB_AV7110)` builds `dvb-ttpci.o`, and `obj-$(CONFIG_DVB_SP8870)` builds `sp8870.o`.

## Control Flow
Kbuild uses the object list to form the module or built-in object based on Kconfig symbols.

## State and Persistence Behavior
No runtime state.

## Dependencies and Integration Points
Adds include paths for DVB frontends, tuners, PCI TTP CI, and common media code, matching headers consumed by `av7110.c`.

## Risks
Object order and include paths matter for optional features and shared local headers. Removing `av7110_hw.o` or `av7110_av.o` breaks exported symbols used by the main driver.

## Test Signals
Successful compile/link for all Kconfig combinations, especially with `CONFIG_DVB_AV7110_IR` toggled.
