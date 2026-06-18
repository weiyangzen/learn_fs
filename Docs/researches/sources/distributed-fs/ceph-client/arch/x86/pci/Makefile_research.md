# sources/distributed-fs/ceph-client/arch/x86/pci/Makefile

## Purpose
Defines the x86 PCI support object composition for the kernel build. It selects core PCI initialization/resource files and conditionally includes BIOS, MMCONFIG, direct config access, platform quirks, and x86 platform-specific PCI backends.

## Important build rules
- Always builds `i386.o`, `init.o`, `fixup.o`, `legacy.o`, `irq.o`, `common.o`, `early.o`, and `bus_numa.o`.
- Adds `pcbios.o` for `CONFIG_PCI_BIOS`.
- Adds `mmconfig_$(BITS).o`, `direct.o`, and `mmconfig-shared.o` for `CONFIG_PCI_MMCONFIG`.
- Adds `direct.o` for `CONFIG_PCI_DIRECT`; this can overlap with MMCONFIG selection.
- Adds `olpc.o`, `xen.o`, `acpi.o`, `ce4100.o`, `intel_mid.o`, `numachip.o`, `amd_bus.o`, and `broadcom_bus.o` based on platform/config symbols.
- Adds `-DDEBUG` when `CONFIG_PCI_DEBUG` is enabled.

## Control flow and integration
This file has no runtime control flow. Its build-time decisions determine which PCI probing and access methods can register at boot. For this subset, it wires `acpi.c`, `amd_bus.c`, `broadcom_bus.c`, `bus_numa.c`, `ce4100.c`, `common.c`, `direct.c`, and `early.c` into the arch PCI subsystem.

## State and persistence
No runtime state is stored here. Build configuration determines which object files become part of the kernel image.

## Dependencies and integration points
Depends on Kbuild `obj-y`/`obj-*` semantics and config symbols under PCI, ACPI, x86 platform, Xen, OLPC, AMD NB, and Broadcom CNB20LE quirk options.

## Risks and test signals
Duplicate inclusion of `direct.o` is controlled by Kbuild object de-duplication, but config changes should be checked for unexpected missing config access backends. Build tests across `CONFIG_PCI_MMCONFIG`, `CONFIG_PCI_DIRECT`, `CONFIG_ACPI`, 32-bit/64-bit, and platform options are the main validation signal.
