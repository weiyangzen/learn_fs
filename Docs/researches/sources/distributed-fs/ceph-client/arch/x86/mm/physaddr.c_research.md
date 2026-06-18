# sources/distributed-fs/ceph-client/arch/x86/mm/physaddr.c

## Purpose
`physaddr.c` validates and translates kernel virtual addresses to physical addresses on x86, with DEBUG_VIRTUAL checks that catch invalid direct-map, vmalloc, fixmap, and high-kernel-map use.

## Important APIs, Types, and Functions
On DEBUG_VIRTUAL builds it exports `__phys_addr()`. All builds export `__virt_addr_valid()`. x86-64 handles both `__START_KERNEL_map` image addresses and direct-map addresses using `phys_base`; x86-32 handles `PAGE_OFFSET` direct-map addresses and rejects vmalloc/fixmap ranges.

## Control Flow and State
x86-64 translation subtracts `__START_KERNEL_map` and uses carry-style comparisons to distinguish high kernel image aliases from direct-map addresses, then validates the resulting physical address and PFN. x86-32 DEBUG_VIRTUAL translation checks that the virtual address is above `PAGE_OFFSET`, not vmalloc once the vmalloc base is set, and within `max_low_pfn`, then cross-checks `slow_virt_to_phys()`.

## State and Persistence
No state is owned here. The functions read `phys_base`, `KERNEL_IMAGE_SIZE`, `max_low_pfn`, `__vmalloc_start_set`, and memmap PFN validity.

## Dependencies and Integration Points
It depends on `phys_addr_valid()` from `physaddr.h`, `pfn_valid()`, vmalloc address classification, and architecture virtual layout constants. It supports `virt_addr_valid()` users across MM, drivers, and debug code.

## Risks and Test Signals
Risks include accepting non-direct-map virtual addresses, rejecting valid highmap aliases under KASLR, and stale `max_low_pfn` assumptions very early in boot. Test signals are DEBUG_VIRTUAL warnings for bad `__pa()` users, boot on KASLR/non-KASLR kernels, vmalloc rejection tests, and highmem/direct-map validation paths.
