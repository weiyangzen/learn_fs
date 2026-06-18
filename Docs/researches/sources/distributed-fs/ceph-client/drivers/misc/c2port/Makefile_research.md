# sources/distributed-fs/ceph-client/drivers/misc/c2port/Makefile

## Purpose
`c2port/Makefile` maps C2 Kconfig symbols to object files.

## Important APIs, Types, and Functions
`obj-$(CONFIG_C2PORT) += core.o` builds the generic C2 class and sysfs programming engine. `obj-$(CONFIG_C2PORT_DURAMAR_2150) += c2port-duramar2150.o` builds the Duramar I/O-port backend.

## Control Flow
Kbuild includes each object when the corresponding symbol is `y` or `m`. The core exports `c2port_device_register()` and `c2port_device_unregister()` for board/client modules.

## State and Persistence
The file has no runtime state. It controls which modules or built-in objects exist.

## Dependencies and Integration Points
It integrates with the Linux Kbuild system and the Kconfig symbols in the same directory.

## Risks and Edge Cases
If the Duramar object is built without a loadable or built-in core, symbol resolution would fail; the Kconfig nesting normally prevents that.

## Test Signals
Build matrix coverage should verify `CONFIG_C2PORT=y/m` and `CONFIG_C2PORT_DURAMAR_2150=y/m` combinations produce the expected objects and exported-symbol resolution.
