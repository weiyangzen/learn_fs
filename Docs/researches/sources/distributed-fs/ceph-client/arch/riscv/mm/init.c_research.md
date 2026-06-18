<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/init.c -->
# sources/distributed-fs/ceph-client/arch/riscv/mm/init.c

## Purpose
`init.c` is the main RISC-V memory initialization file. It builds early and final page tables, establishes kernel and linear mappings, handles KASLR/relocation, reserves boot memory, initializes zones, vmemmap, execmem ranges, and memory hotplug mapping removal.

## Important APIs, Types, And Functions
Important globals include `kernel_map`, `satp_mode`, `pgtable_l4_enabled`, `pgtable_l5_enabled`, `phys_ram_base`, `new_vmalloc`, and page-table roots. Key functions include `arch_mm_preinit()`, `setup_bootmem()`, `relocate_kernel()`, `__set_fixmap()`, page-table allocation/mapping helpers, `set_satp_mode()`, `setup_vm()`, `create_kernel_page_table()`, `setup_vm_final()`, `paging_init()`, `misc_mem_init()`, `vmemmap_populate()`, `pgtable_cache_init()`, `execmem_arch_setup()`, and memory hotplug add/remove helpers.

## Control Flow
Early setup computes kernel virtual/physical offsets, optional KASLR, SATP mode, early fixmap/trampoline mappings, kernel mappings, and FDT fixmap before enabling final allocation helpers. Bootmem reserves kernel, initrd, DTB, reserved-memory regions, crashkernel, DMA limits, and contiguous DMA. Final setup creates swapper mappings for fixmap, linear memory, kernel text/rodata with strict permissions, KASAN shadow, switches SATP, flushes TLBs, and moves to late page-table allocation. Hotplug paths add/remove linear and vmemmap mappings and free empty page-table pages.

## State And Persistence
Persistent runtime state is kernel page tables, memblock reservations during boot, zone PFNs, vmemmap mappings, SATP mode, page-table level enable flags, and execmem range metadata. These are in-memory kernel state only.

## Dependencies And Integration Points
It integrates with memblock, FDT/ACPI reserved memory, KASAN, KFENCE, SWIOTLB, crashkernel, NUMA, sparsemem/vmemmap, set_memory, execmem/BPF/modules, TLB flushes, and RISC-V boot head code.

## Risks
This is boot-critical. Alignment of kernel, PAGE_OFFSET, fixmap, and huge mappings is enforced by BUG_ONs. Page-table level downgrade must match valid virtual addresses and DTB accessibility. Strict RWX, KASAN, relocation, and hotplug all alter mappings and can expose subtle alias/TLB bugs.

## Test Signals
Boot matrix across Sv39/Sv48/Sv57, 32-bit, KASLR, relocatable, KASAN, KFENCE, strict RWX, sparsemem, crashkernel, memory hotplug, and module/BPF execmem tests is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/mm/init.c -->
