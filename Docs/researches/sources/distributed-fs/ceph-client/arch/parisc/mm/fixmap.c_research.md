# sources/distributed-fs/ceph-client/arch/parisc/mm/fixmap.c

Purpose: provides PA-RISC fixed-address mapping updates for kernel subsystems that need temporary or special virtual mappings.

Important APIs: `set_fixmap(enum fixed_addresses idx, phys_addr_t phys)` installs a `PAGE_KERNEL_RWX` PTE for the fixed virtual address. `clear_fixmap(enum fixed_addresses idx)` clears that PTE. Both are `notrace`, appropriate for low-level contexts.

Control flow: `set_fixmap()` converts the fixed index to a virtual address, walks the kernel page table to the PTE, writes a physical mapping with `set_pte_at()`, and flushes the one-page kernel TLB range. `clear_fixmap()` obtains the kernel PTE via `virt_to_kpte()`, warns if already empty, clears it, and flushes the same range.

State and persistence: mutates `init_mm` kernel page tables. The mapping persists until explicitly cleared or overwritten. TLB flushes synchronize CPU translation state.

Dependencies and integration: depends on `fixmap_init()` in `init.c` having allocated the fixmap page-table range. Includes cache/TLB and fixmap architecture headers. Used by architecture features needing stable high virtual slots.

Risks: always using RWX permissions is broad and may conflict with strict W/X expectations. Missing flushes would leave stale translations. Calling before `fixmap_init()` would dereference missing page tables.

Test signals: set and clear representative fixed indices, verify physical translation and permissions, detect double clear warning, check TLB invalidation on all relevant CPUs, and test under kprobe/tracing-disabled contexts.
