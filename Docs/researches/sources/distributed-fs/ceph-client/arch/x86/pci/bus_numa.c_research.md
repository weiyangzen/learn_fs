# sources/distributed-fs/ceph-client/arch/x86/pci/bus_numa.c

## Purpose
Maintains a shared list of hardware-probed PCI root bus descriptors, including bus ranges, NUMA node/link identifiers, and root resources. It is used by AMD and Broadcom native probes and consumed by ACPI/common root scanning as fallback topology/resource information.

## Important APIs and functions
- `LIST_HEAD(pci_root_infos)` is the global root-info registry.
- `x86_pci_root_bus_node()` returns a NUMA node for a root bus or `NUMA_NO_NODE`.
- `x86_pci_root_bus_resources()` appends hardware-probed resources for a root bus, or defaults to global `ioport_resource` and `iomem_resource`.
- `alloc_pci_root_info()` allocates and initializes a root descriptor.
- `update_res()` adds or merges a root resource.

## Control flow
Native probes allocate entries with a bus range and later add IO/MMIO resources. Root scan code asks for the node and resource list by root bus number. If an entry exists, `x86_pci_root_bus_resources()` ensures an `IORESOURCE_BUS` window is present and appends each recorded resource. If no entry exists, it falls back to legacy global IO and memory resources.

## State and persistence
All state lives in the boot-lifetime `pci_root_infos` linked list. Each `pci_root_info` owns a linked list of dynamically allocated `pci_root_res` records. `update_res()` can merge adjacent/overlapping resources with identical flags.

## Dependencies and integration points
Depends on Linux resource/list APIs and the local `bus_numa.h` structures. Integrated with `amd_bus.c`, `broadcom_bus.c`, `acpi.c`, and `common.c`.

## Risks and edge cases
The lookup matches `info->busn.start == bus`, so overlapping or non-start bus queries will not match. Resource merging uses inclusive ranges and must avoid overflow around `common_end + 1`. The fallback to entire IO/memory resources is broad but preserves historical behavior when no native bridge data exists.

## Test signals
Boot logs should distinguish `hardware-probed resources` from `using default resources`. Validate that native bridge probes create one root entry per root bus and that resources are not duplicated when ACPI has already supplied a bus resource.
