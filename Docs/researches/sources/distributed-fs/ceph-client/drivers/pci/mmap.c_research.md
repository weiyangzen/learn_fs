# sources/distributed-fs/ceph-client/drivers/pci/mmap.c

## Purpose
Implements generic PCI resource mmap support for sysfs/procfs paths on architectures that use the generic PCI mmap helpers.

## Important APIs, Types, and Functions
The file conditionally defines `pci_mmap_resource_range()` and `pci_mmap_fits()`. It also defines `pci_phys_vm_ops` with optional `generic_access_phys`.

## Control Flow
`pci_mmap_resource_range()` validates that the requested VMA page range fits inside the BAR, chooses device or write-combining page protection, converts I/O BAR offsets through `pci_iobar_pfn()` or memory BAR offsets by adding the BAR start PFN, attaches physical VM ops, and calls `io_remap_pfn_range()`. `pci_mmap_fits()` checks whether a requested sysfs/procfs mmap page range lies within the PCI resource, using `pci_resource_to_user()` for procfs address semantics.

## State and Persistence Behavior
The file stores no persistent state. It modifies VMA page offset, page protection, and VM ops for the mapping lifetime.

## Dependencies and Integration Points
Depends on architecture config symbols, mm/VMA APIs, PCI resource helpers, `pci_iobar_pfn()`, and optional sysfs/procfs mmap interfaces.

## Risks
Incorrect page-range validation could expose memory outside a BAR. I/O BAR and memory BAR offset semantics differ between sysfs and procfs. Write-combining mappings change ordering and must be requested intentionally.

## Test Signals
Mmap memory and I/O BARs through sysfs/procfs, reject over-length VMAs, validate write-combine protection, test `generic_access_phys` if enabled, and verify procfs address conversion.
