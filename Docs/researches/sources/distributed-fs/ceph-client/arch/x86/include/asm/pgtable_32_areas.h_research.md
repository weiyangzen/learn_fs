# sources/distributed-fs/ceph-client/arch/x86/include/asm/pgtable_32_areas.h

Purpose: defines 32-bit x86 virtual address ranges for vmalloc, kmap/PKMAP, LDT remap, CPU entry area, modules, and maximum low memory.

Important APIs, types, and functions: key macros are `VMALLOC_OFFSET`, `VMALLOC_START`, `LAST_PKMAP`, `CPU_ENTRY_AREA_PAGES`, `CPU_ENTRY_AREA_BASE`, `LDT_BASE_ADDR`, `LDT_END_ADDR`, `PKMAP_BASE`, `VMALLOC_END`, `MODULES_VADDR`, `MODULES_END`, `MODULES_LEN`, and `MAXMEM`. It declares `__vmalloc_start_set`.

Control flow: no functions are implemented. Constants are derived from `high_memory`, fixmap totals, CPU entry area size, PAE/highmem configuration, and vmalloc reserve.

State and persistence: `__vmalloc_start_set` records when `high_memory` is available. The rest are virtual layout calculations.

Dependencies and integration points: depends on `cpu_entry_area.h`, fixmap layout, highmem PKMAP users, vmalloc, module loader, and LDT/PTI remap code.

Risks: ranges are tightly packed near fixmap on 32-bit kernels. Off-by-one or ordering mistakes can overlap vmalloc, PKMAP, LDT, CPU entry area, modules, or reserved holes. `MODULES_LEN` is defined as `MODULES_VADDR - MODULES_END`, which callers must treat carefully because the range endpoints are unusual on 32-bit.

Test signals: boot with highmem and non-highmem, vmalloc stress, module loading, kmap/PKMAP use, CPU entry area mapping for all CPUs, LDT use under PTI, and address-range assertions/debug page-table dumps.
