# sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.h

## Purpose
Declares the shared data structures and helper prototypes used for x86 native PCI root bus NUMA/resource discovery.

## Important APIs and types
- `struct pci_root_res` wraps a `struct resource` in a linked-list node.
- `struct pci_root_info` stores list linkage, a short name, resource list, bus-number resource, NUMA node, and AMD link ID.
- `pci_root_infos` is the external global list.
- `alloc_pci_root_info()` allocates a root descriptor.
- `update_res()` adds or merges resources into a descriptor.

## Control flow, state, and dependencies
This header has no executable control flow. It defines the contract between resource producers (`amd_bus.c`, `broadcom_bus.c`) and consumers (`bus_numa.c`, ACPI/common scan paths). State is owned by the implementation file and dynamically allocated records.

## Risks and test signals
The fixed `name[12]` fits names like `PCI Bus #ff`; callers should not write longer names. The comment notes transparent subordinate buses need enough resource entries from root resources. Compile coverage across users is the main validation signal.
