# sources/distributed-fs/ceph-client/mm/early_ioremap.c

## Purpose
`early_ioremap.c` provides generic early-boot temporary mapping helpers for architectures that need to access physical I/O or memory before the normal `ioremap()` and `vmalloc` infrastructure is ready. It maps physical ranges through fixed-address boot-time slots and also supplies simple no-MMU identity mappings.

## Important APIs, types, and functions
The MMU path exports `early_ioremap_setup()`, `early_ioremap_reset()`, `early_ioremap()`, `early_memremap()`, `early_memremap_ro()`, optional `early_memremap_prot()`, `copy_from_early_mem()`, `early_iounmap()`, and `early_memunmap()`. The weak `early_memremap_pgprot_adjust()` lets architectures adjust protections. The central helper is `__early_ioremap()`, which reserves a slot from `prev_map[]`, page-aligns the physical range, installs fixed mappings with `__early_set_fixmap()` or `__late_set_fixmap()`, and returns the virtual address plus original offset.

## Control flow
`early_ioremap_setup()` initializes `slot_virt[]` from `FIX_BTMAP_BEGIN` and the per-slot fixed-map stride. `__early_ioremap()` finds a free slot, rejects zero or wrapping ranges, records the caller-visible size in `prev_size[]`, page-aligns the physical address and size, rejects mappings larger than `NR_FIX_BTMAPS`, installs one fixed mapping per page, and records the returned pointer in `prev_map[]`. `early_iounmap()` finds the matching slot by exact returned address, checks the size matches, computes the page count from the virtual offset and original size, clears the fixed mappings, and releases the slot.

`copy_from_early_mem()` copies an arbitrary physical range by repeatedly mapping chunks no larger than the fixed-map capacity, copying out of the mapped window, and unmapping. `check_early_ioremap_leak()` runs as a late initcall and warns if any slot remains mapped.

## State and persistence
The MMU implementation has `__initdata` state only: `early_ioremap_debug`, `after_paging_init`, `prev_map[]`, `prev_size[]`, and `slot_virt[]`. Mappings are temporary boot-time state and should be unmapped before late init. After `early_ioremap_reset()`, architectures that support late use must provide `__late_set_fixmap()` and `__late_clear_fixmap()`; otherwise the weak defaults call `BUG()`.

## Dependencies and integration points
The file depends on architecture fixmap definitions (`FIX_BTMAP_BEGIN`, `NR_FIX_BTMAPS`, `FIX_BTMAPS_SLOTS`, page protection constants), early fixmap functions, initcall ordering, `system_state`, and optional architecture protection overrides. It is used by early platform, firmware, memory discovery, and boot code that needs temporary physical access before full mapping services exist.

## Risks and test signals
Risks include leaking slots, mismatched unmap sizes, mapping ranges larger than the fixed-map window, physical address wraparound, and using late mappings on an architecture that did not implement late fixmap operations. Since unmap lookup is by exact returned pointer, callers must preserve the pointer and size. Test signals include booting with `early_ioremap_debug`, absence of late leak warnings, successful early firmware/table copies, and architecture boot tests that exercise both pre- and post-`paging_init()` use if supported. The no-MMU path should remain a simple identity mapping with no slot state.
