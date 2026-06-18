# sources/distributed-fs/ceph-client/arch/xtensa/mm/init.c

Purpose: Initializes physical memory accounting, zones, VM layout reporting, `memmap=` parsing, and MMU protection mappings.

Important APIs, types, and functions: `bootmem_init()`, `print_vm_layout()`, `arch_zone_limits_init()`, `zones_init()`, `parse_memmap_one()`, `parse_memmap_opt()`, `protection_map`, and `DECLARE_VM_GET_PAGE_PROT`.

Control flow: `bootmem_init()` reserves unusable low memory/page zero, scans reserved FDT memory, validates DRAM, computes PFN bounds, runs early memtest, sets memblock allocation limit, reserves CMA, and dumps memblock. `memmap=` parsing adds or reserves regions with `size@addr`, `size$addr`, or reserves from `size` to the end. Zone setup reports layout and sets normal/highmem limits.

State and persistence: Mutates memblock reservations and memory regions, global PFN bounds, zone limits, and page protection lookup table.

Dependencies and integration: Called from `setup_arch()`, uses FDT reserved memory, DMA contiguous reservation, early params, section symbols, highmem constants, and generic VM protection APIs.

Risks: Bad memmap syntax can silently leave memory unchanged except warnings; reserving `mem_size, -mem_size` depends on unsigned wrap semantics; PFN calculations must respect `PHYS_OFFSET` and `MAX_LOW_PFN`.

Test signals: Boot memory map logs, `memmap=` add/reserve cases, no-memory panic path, highmem zone setup, CMA reservation, and executable/non-executable mmap protection bits.
