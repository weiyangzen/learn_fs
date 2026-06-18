# sources/distributed-fs/ceph-client/drivers/comedi/Kconfig

## Purpose

`drivers/comedi/Kconfig` defines the build configuration for the COMEDI data acquisition subsystem: core module, debug option, default async buffer sizes, bus-family menus, hardware drivers, shared helper modules, and COMEDI unit tests.

## APIs And Flow

`menuconfig COMEDI` gates the file. `COMEDI_DEFAULT_BUF_SIZE_KB` and `COMEDI_DEFAULT_BUF_MAXSIZE_KB` feed defaults used by `comedi_fops.c`. Bus menus cover misc, ISA/PC104, PCI, PCMCIA, and USB drivers. Hidden helpers include `COMEDI_8254`, `COMEDI_8255`, `COMEDI_KCOMEDILIB`, `COMEDI_ISADMA`, `COMEDI_MITE`, `COMEDI_NI_TIO`, `COMEDI_NI_TIOCMD`, and `COMEDI_NI_ROUTING`. `depends on` clauses enforce bus/API availability; `select` clauses pull shared helpers.

## State, Dependencies, Risks, Tests

There is no runtime state, but selected tristates persist in kernel config and decide compiled modules, debug flags, and default buffer constants. It integrates with the COMEDI Makefile and driver subdirectories. Risks are missing selects, over-broad dependencies, stale help text, and drivers lacking required HAS_IOPORT/HAS_DMA gates. Test allmodconfig, allyesconfig, randconfig, bus-disabled builds, and COMEDI_TESTS.
