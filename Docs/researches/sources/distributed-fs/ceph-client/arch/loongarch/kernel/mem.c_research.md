## sources/distributed-fs/ceph-client/arch/loongarch/kernel/mem.c

### Purpose
`mem.c` seeds the early memblock allocator from EFI memory descriptors on LoongArch. It classifies usable and reserved firmware regions, reserves low memory and kernel image ranges, establishes PFN limits, and assigns all memory and reserved memblocks to node 0 before later NUMA setup may refine ownership.

### Important APIs, Types, And Functions
The file contains `memblock_init`. It iterates `for_each_efi_memory_desc`, reads `efi_memory_desc_t` fields, calls `memblock_add`, `memblock_reserve`, `memblock_set_current_limit`, and `memblock_set_node`, and updates `max_pfn` and `max_low_pfn`.

### Control Flow
Usable EFI types such as loader, boot-service, persistent, and conventional memory are added to memblock. PAL, unusable, and ACPI reclaim memory are added and then intentionally fall through to reserve them. Reserved/runtime/MMIO types are reserved without being added as normal RAM. After descriptor parsing, the first 2 MiB, the kernel text/data/bss range, and highmem limit are reserved/configured.

### State, Persistence, And Dependencies
The persistent boot state is the memblock memory and reserved region lists that drive page allocator initialization. It depends on EFI initialization having populated the memory map and on `_text`, `_end`, `PHYS_OFFSET`, `HIGHMEM_START`, and LoongArch physical-address helpers being correct.

### Integration Points
`setup_arch` calls `memblock_init` before page table and platform initialization. Later setup code applies `mem=` overrides, crashkernel/initrd reservations, NUMA coverage validation, resources, CMA, SWIOTLB, and memtest based on these memblock lists.

### Risks
Firmware memory classification mistakes can expose reserved/runtime memory to the allocator or hide usable RAM. The deliberate fallthrough for PAL/unusable/ACPI reclaim memory is important; removing it would add those regions as free. Reserving only the first 2 MiB assumes the platform's low-memory hazards fit that range.

### Test Signals
Boot with EFI memory-map debug and compare `/proc/iomem` against firmware. Test ACPI reclaim/unusable regions, highmem boundaries, `mem=` overrides, crashkernel reservations, and boot on systems with persistent memory descriptors.
