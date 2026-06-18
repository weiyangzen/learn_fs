<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_cache.c -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_cache.c

## Purpose
`eeh_cache.c` implements the PCI I/O address cache used by EEH to map an MMIO or I/O token back to the owning `eeh_dev` quickly, including from interrupt context.

## Important APIs, Types, And Functions
The private `struct pci_io_addr_range` stores an RB-tree node, address range, `eeh_dev`, `pci_dev`, and resource flags. Public functions are `eeh_addr_cache_get_dev()`, `eeh_addr_cache_insert_dev()`, `eeh_addr_cache_rmv_dev()`, `eeh_addr_cache_init()`, and `eeh_cache_debugfs_init()`. Internal helpers handle RB lookup, insert, remove, and debug printing/showing.

## Control Flow
Lookup takes `piar_lock`, walks the RB tree by comparing the requested address with `addr_lo/addr_hi`, and returns the matching `eeh_dev`. Insert skips devices without EEH PEs, walks standard BAR and ROM resources, filters invalid or non-I/O/MEM resources, and inserts non-overlapping ranges. Removal walks the tree repeatedly, erasing all entries for a PCI device. Debugfs renders the tree under the same lock.

## State And Persistence
State is a global RB tree protected by a spinlock. Entries are allocated with `GFP_ATOMIC` and freed on device removal. The cache is runtime-only.

## Dependencies And Integration Points
It integrates with PCI resources, `pci_dev_to_eeh_dev()`, EEH probe/remove, `eeh_check_failure()`, debugfs, and PowerPC PCI bridge metadata.

## Risks
Overlapping BAR ranges are warned and return the existing entry, which can hide ambiguous ownership. Removal is intentionally O(n * resources). Entries hold raw pointers and depend on remove hooks running before devices disappear.

## Test Signals
Signals include address-cache debugfs output, successful lookup after MMIO all-ones reads, insertion/removal during PCI hotplug, no stale pointers after remove, and warnings for overlapping resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/eeh_cache.c -->
