# sources/distributed-fs/ceph-client/drivers/gpib/ines/Makefile

## Purpose

This Kbuild fragment builds the INES GPIB board driver when `CONFIG_GPIB_INES` is enabled.

## Important APIs and Targets

- `obj-$(CONFIG_GPIB_INES) += ines_gpib.o` compiles `ines_gpib.c` into the kernel/module object selected by the config symbol.

## Control Flow and Integration

Kbuild includes this file from the parent GPIB driver Makefile. The resulting object contains PCI, ISA, and optional PCMCIA INES support plus its gpib-interface registrations.

## State and Persistence Behavior

No runtime state exists.

## Dependencies

The Makefile depends on the kernel Kconfig symbol `CONFIG_GPIB_INES` and on `ines_gpib.c` plus headers in the same and include directories.

## Risks and Test Signals

Build coverage should verify enabled and disabled config cases. A missing parent Makefile entry or Kconfig symbol mismatch would prevent the driver from building even if this fragment is correct.
