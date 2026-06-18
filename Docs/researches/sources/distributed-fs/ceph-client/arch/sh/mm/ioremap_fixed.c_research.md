# sources/distributed-fs/ceph-client/arch/sh/mm/ioremap_fixed.c

Purpose: supplies early boot fixed-slot ioremap before normal vmalloc/ioremap infrastructure is usable.

Important state and APIs: `struct ioremap_map`, `ioremap_maps[FIX_N_IOREMAPS]`, `ioremap_fixed_init`, `ioremap_fixed`, and `iounmap_fixed`.

Control flow: initialization records virtual addresses for fixed slots. `ioremap_fixed` page-aligns physical ranges, finds a free slot, checks capacity, installs wired fixmap PTEs, and returns an offset-adjusted address. `iounmap_fixed` finds the mapping, clears fixmap entries in reverse, and frees the slot.

State and persistence: maintains a small in-memory table of active fixed mappings and wired fixmap PTE/TLB entries.

Dependencies and integration: used by `ioremap.c` before `mem_init_done`, depends on fixmap, memblock-era page tables, TLB/cache helpers, and `_PAGE_WIRED`.

Risks: slot allocation stores only the first slot but can map multiple pages, so overlapping multi-page slot accounting must be treated carefully. Returning `NULL` without clearing partial state would be hazardous if future edits add partial failure paths.

Test signals: early boot devices using ioremap, fixed-slot exhaustion tests, and unmap/remap cycles before normal ioremap.
