# sources/distributed-fs/ceph-client/arch/x86/mm/amdtopology.c

## Purpose
Discovers AMD NUMA topology directly from northbridge PCI configuration registers during early boot and registers memory ranges per node.

## Important APIs, Types, And Functions
`amd_numa_init()` is the exported initialization entry. `find_northbridge()` scans bus 0 devices for supported AMD function IDs. Static `nodeids[8]` records node IDs from DRAM limit registers.

## Control Flow
The code checks early PCI access, finds the northbridge, reads node count from config register `0x60`, then iterates up to eight DRAM base/limit pairs. It skips disabled/excess/empty/interleaved entries, clamps ranges to `[0,max_pfn)`, enforces sorted bases, calls `numa_add_memblk()`, and sets `numa_nodes_parsed`. After valid memory nodes are found, it maps APIC IDs to nodes based on core-domain size.

## State And Persistence
Mutates global NUMA parse state, memory-block descriptors, and APIC-ID-to-node mappings during `__init`. `nodeids` is `__initdata`.

## Dependencies And Integration Points
Depends on direct PCI config access, memblock/numa_memblks, E820-derived PFN limits, topology domain sizing, and APIC mapping helpers. Used when `CONFIG_AMD_NUMA` is enabled.

## Risks
Northbridge register interpretation is hardware-specific. Interleaved memory is rejected. The APIC mapping assumes contiguous APIC IDs by node and core-domain size. Invalid BIOS register order or limits aborts NUMA setup.

## Test Signals
Boot logs on AMD NUMA systems, disabled/interleaved/malformed node register cases, APIC-to-node validation, memblock NUMA ranges, and fallback behavior when early PCI is unavailable.
