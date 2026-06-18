# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/grackle.h

Purpose: Declares setup support for the Apple/Motorola Grackle PCI host bridge on PowerPC platforms.

Important APIs, types, and functions: Exposes `setup_grackle(struct pci_controller *hose)` when building the kernel and includes the PCI bridge controller type.

Control flow: Platform PCI setup code detects a Grackle host bridge, initializes the `pci_controller`, then calls `setup_grackle()` for bridge-specific configuration.

State and persistence: No state is stored in the header. Bridge configuration is applied to PCI/host-bridge registers by implementation code.

Dependencies and integration points: Depends on `asm/pci-bridge.h` and old PowerMac/CHRP PCI initialization paths.

Risks: The header is tiny but architecture-specific. Wrong bridge setup can affect all PCI config and I/O windows under the host bridge.

Test signals: Boot PCI enumeration on Grackle-based machines or emulators, config-space reads/writes, legacy I/O window setup, and build coverage for old PowerPC platform options.
