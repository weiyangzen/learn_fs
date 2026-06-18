# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/Makefile

## Purpose
`ddbridge/Makefile` defines how the Digital Devices bridge driver is compiled and linked inside the kernel media tree.

## Important APIs, Types, And Functions
`ddbridge-objs` aggregates `ddbridge-main.o`, `ddbridge-core.o`, `ddbridge-ci.o`, `ddbridge-hw.o`, `ddbridge-i2c.o`, `ddbridge-max.o`, `ddbridge-mci.o`, and `ddbridge-sx8.o` into the `ddbridge` module. `obj-$(CONFIG_DVB_DDBRIDGE)` builds `ddbridge.o` and `ddbridge-dummy-fe.o`. `ccflags-y` adds include paths for `drivers/media/dvb-frontends/` and `drivers/media/tuners/`.

## Control Flow
There is no runtime control flow. Kbuild uses the object list and config symbol to decide module composition and compile include search paths.

## State, Persistence, And Dependencies
Persistent state is build metadata. The Makefile depends on Kbuild variables, the Kconfig symbol `CONFIG_DVB_DDBRIDGE`, and source/header availability in the frontend and tuner directories.

## Integration Points
`ddbridge-ci.c` is one component of the linked module, so CI support is always part of `ddbridge.o` when the driver is built. `ddbridge-dummy-fe.o` is built alongside the main module under the same config symbol.

## Risks
Forgetting to add new implementation objects here leads to link errors or missing functionality. Include-path changes can mask missing qualified includes. Splitting optional features would require matching Kconfig symbols and conditional object rules.

## Test Signals
Build the driver as built-in and module, verify all listed object files compile, run `modinfo ddbridge` on module builds, and ensure frontend/tuner headers resolve without relying on accidental global include paths.
