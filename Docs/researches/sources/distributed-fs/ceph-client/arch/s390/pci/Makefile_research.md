## sources/distributed-fs/ceph-client/arch/s390/pci/Makefile

Purpose: declares the s390 PCI subsystem object composition for Kbuild.

Important APIs, types, and functions: when `CONFIG_PCI` is enabled it builds core files including `pci.o`, IRQ, CLP, event, debug, instruction, MMIO, bus, KVM hook, report, and fixup support. `CONFIG_PCI_IOV` adds SR-IOV support through `pci_iov.o`; `CONFIG_SYSFS` adds `pci_sysfs.o`.

Control flow: no runtime behavior; Kbuild conditionals select objects.

State and persistence: no runtime state. Build state determines which s390 PCI features exist in the kernel image.

Dependencies and integration points: integrates PCI core support with optional SR-IOV and sysfs layers. `pci.o` depends on the companion objects listed here for IRQ setup, CLP scanning, bus registration, MMIO, and diagnostics.

Risks: missing companion objects would break unresolved symbols or silently drop PCI features. Config guards must stay aligned with source-level `#ifdef`s and exported hooks.

Test signals: build coverage for `CONFIG_PCI=y/n`, `CONFIG_PCI_IOV=y/n`, and `CONFIG_SYSFS=y/n`, plus link validation of the full s390 PCI subsystem.
