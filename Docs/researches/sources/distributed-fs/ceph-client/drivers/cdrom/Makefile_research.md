# sources/distributed-fs/ceph-client/drivers/cdrom/Makefile

## Purpose
The cdrom Makefile selects the uniform CD-ROM core and GD-ROM driver objects from Kconfig symbols.

## Important APIs, Types, And Functions
`obj-$(CONFIG_CDROM) += cdrom.o` builds the uniform CD-ROM layer. `obj-$(CONFIG_GDROM) += gdrom.o` builds the GD-ROM driver.

## Control Flow
Kbuild includes each object when its configuration symbol is enabled. The uniform layer can be built into the kernel or as a module depending on `CONFIG_CDROM`.

## State And Persistence
There is no runtime state; it affects build outputs only.

## Dependencies And Integration Points
The mapping is used by low-level optical drivers that link against exported symbols in `cdrom.o`.

## Risks And Edge Cases
Build failures would occur if `CONFIG_GDROM` or `CONFIG_CDROM` are enabled but the corresponding source or exported dependencies are missing. Because many drivers use the uniform layer, accidental omission of `cdrom.o` breaks broad optical-drive functionality.

## Test Signals
Build with `CONFIG_CDROM=y/m`, with `CONFIG_GDROM` enabled, and with CD-ROM disabled to verify expected objects are included or omitted.
