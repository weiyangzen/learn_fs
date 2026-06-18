# sources/distributed-fs/ceph-client/include/uapi/linux/pci.h

Purpose: Publishes basic PCI userspace helpers, legacy `/proc/bus/pci` ioctl values, and hotplug event IDs.

Important APIs/types/functions: Exports `PCI_DEVFN(slot, func)`, `PCI_SLOT(devfn)`, `PCI_FUNC(devfn)`, `PCIIOC_CONTROLLER`, `PCIIOC_MMAP_IS_IO`, `PCIIOC_MMAP_IS_MEM`, `PCIIOC_WRITE_COMBINE`, and `enum pci_hotplug_event`. It includes `<linux/pci_regs.h>` for register definitions.

Control flow: Userspace and kernel code encode or decode slot/function numbers with the macros. Legacy tools issue PCIIOC ioctls to change mmap space or query controller data for `/proc/bus/pci/X/Y` nodes. Hotplug events communicate link/card presence changes.

State and persistence behavior: The header owns no state. It describes addressing and ioctl commands that operate on kernel PCI device state and mmap behavior.

Dependencies and integration points: Depends on `pci_regs.h`. Integrates with pciutils-style tooling, legacy procfs PCI access, hotplug agents, and PCI core definitions.

Risks: `PCI_DEVFN` masks slot/function bits, so callers must validate inputs before encoding. Legacy mmap ioctls can expose device MMIO/IO space and require appropriate permissions.

Test signals: Compile pciutils consumers, encode/decode representative devfns, exercise procfs PCI mmap mode selection where enabled, and verify hotplug event constants in user/kernel ABI tests.
