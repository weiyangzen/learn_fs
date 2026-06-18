# sources/distributed-fs/ceph-client/drivers/comedi/Makefile

## Purpose

`drivers/comedi/Makefile` maps COMEDI Kconfig symbols to Kbuild objects for the core, bus helpers, `kcomedilib`, and low-level drivers.

## APIs And Flow

`ccflags-$(CONFIG_COMEDI_DEBUG)` adds `-DDEBUG`. `comedi-y` aggregates `comedi_fops.o`, `range.o`, `drivers.o`, and `comedi_buf.o`; `proc.o` is conditional on `CONFIG_PROC_FS`. PCI, PCMCIA, and USB bus helpers build from their bus-menu symbols. `obj-$(CONFIG_COMEDI)` builds `comedi.o` and descends into `kcomedilib/` and `drivers/`.

## State, Dependencies, Risks, Tests

There is no runtime state; output persists as built-in code or modules. Dependencies are the Kconfig symbols and object files named here. Risks include omitting core objects, compiling helpers without matching dependencies, or debug flags unexpectedly affecting all COMEDI code. Test `COMEDI=y/m`, `PROC_FS` on/off, and each bus helper as module and built-in.
