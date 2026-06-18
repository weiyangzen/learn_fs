# sources/distributed-fs/ceph-client/arch/sparc/kernel/leon_pci.c

Purpose: Provides the common LEON PCI host-bridge setup routine shared by GRPCI host drivers.

Important APIs/types/functions: `leon_pci_init()` accepts a platform device and `struct leon_pci_info`, allocates a `pci_host_bridge`, attaches I/O, memory, and bus-number resources, assigns parent/sysdata/config ops/IRQ callbacks, scans the root bus, assigns unassigned resources, and adds devices.

Control flow: GRPCI-specific probe code fills `leon_pci_info` with resource windows, config-space ops, bus range, and IRQ mapping. `leon_pci_init()` translates the I/O window so PCI I/O starts at bus address `0x1000`, creates the host bridge, calls `pci_scan_root_bus_bridge()`, then lets generic PCI claim and publish devices.

State and persistence: It owns no global state; persistent state is the allocated PCI host bridge and child PCI devices registered with the kernel.

Dependencies and integration points: It depends on generic Linux PCI host bridge APIs, LEON PCI descriptors from `asm/leon_pci.h`, `pci_common_swizzle`, and platform-device ownership.

Risks and test signals: Resource offset mistakes make I/O BARs unusable, especially because low 4 KB of PCI I/O is intentionally skipped. Test signals include GRPCI1/GRPCI2 enumeration, BAR assignment, IRQ swizzling, resource windows in `/proc/iomem`/sysfs, and allocation failure paths.
