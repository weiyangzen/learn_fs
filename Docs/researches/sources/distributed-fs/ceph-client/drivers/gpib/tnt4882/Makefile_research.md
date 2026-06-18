# sources/distributed-fs/ceph-client/drivers/gpib/tnt4882/Makefile

## Purpose
This Kbuild file builds the National Instruments TNT4882/NAT4882/NEC7210 GPIB driver module when `CONFIG_GPIB_NI_PCI_ISA` is enabled.

## Important APIs, types, and functions
It declares `obj-$(CONFIG_GPIB_NI_PCI_ISA) += tnt4882.o` and composes `tnt4882.o` from `tnt4882_gpib.o` and `mite.o`.

## Control flow
Kbuild links the board driver and MITE PCI helper into one module/built-in object under the NI PCI/ISA config symbol.

## State and persistence behavior
The Makefile has build-time state only. Runtime state is in the compiled C files.

## Dependencies and integration points
It depends on Kbuild and `CONFIG_GPIB_NI_PCI_ISA`. It integrates TNT4882 GPIB code with MITE PCI discovery/window setup required for NI PCI boards.

## Risks and edge cases
Dropping `mite.o` from `tnt4882-objs` would break PCI attach because `tnt4882_gpib.c` calls `mite_init()`, `mite_setup()`, `mite_unsetup()`, and `mite_cleanup()`.

## Test signals
Build with `CONFIG_GPIB_NI_PCI_ISA=y` and `=m`; verify the resulting `tnt4882` object includes both `tnt4882_gpib.o` and `mite.o` symbols.
