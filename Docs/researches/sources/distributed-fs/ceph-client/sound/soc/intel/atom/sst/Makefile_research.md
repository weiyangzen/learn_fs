# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/Makefile

## Purpose
This Kbuild file defines the Atom HiFi2 SST low-level driver modules. It builds a shared core object from common IPC, stream, loader, interface, and helper sources, and builds separate PCI and ACPI enumeration modules.

## Important APIs, types, and functions
`snd-intel-sst-core-y` aggregates `sst.o`, `sst_ipc.o`, `sst_stream.o`, `sst_drv_interface.o`, `sst_loader.o`, and `sst_pvt.o`. `snd-intel-sst-pci-y` adds `sst_pci.o`, and `snd-intel-sst-acpi-y` adds `sst_acpi.o`. The build is controlled by `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM`, `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_PCI`, and `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_ACPI`.

## Control flow
There is no runtime control flow. At build time, Kbuild links the common implementation into `snd-intel-sst-core`, and conditionally builds bus-specific enumeration modules for PCI and ACPI. Runtime entry points come from the source files selected here.

## State and persistence behavior
The Makefile has no runtime state. Its only persistent behavior is the static object composition encoded for Kbuild.

## Dependencies and integration points
It depends on Linux Kbuild and the Kconfig symbols for Atom HiFi2 SST. The object split mirrors runtime responsibilities: `sst.o` core/PM/IRQ, `sst_ipc.o` IPC post/reply, `sst_stream.o` stream commands, `sst_loader.o` firmware load, `sst_pvt.o` helpers, and PCI/ACPI bus probes.

## Risks and edge cases
Missing an object produces unresolved symbols or incomplete driver behavior. Enabling only PCI or ACPI without the core symbol would omit shared implementation. Adding new common helpers requires updating `snd-intel-sst-core-y`.

## Test signals
Build with core only, PCI enabled, ACPI enabled, and both enabled. Verify generated modules link without unresolved symbols and expose expected PCI/ACPI aliases.
