# sources/distributed-fs/ceph-client/arch/powerpc/mm/kasan/book3s_32.c

Purpose: implements Book3S 32-bit KASAN shadow mapping, preferring BAT mappings for large aligned shadow ranges and page tables for the remainder.

Important APIs and control flow: `kasan_init_region()` computes the shadow range, repeatedly finds free BATs and suitable block sizes, allocates physical backing, installs BATs, updates BAT hardware, allocates any remaining backing, initializes shadow page tables, clears early shadow mappings over BAT-backed parts, writes per-page PTEs for the rest, flushes TLBs, and zeroes the shadow.

State and dependencies: state includes BAT entries, `init_mm` page tables, memblock allocations, and early shadow mappings. It depends on `bat_block_size()`, `find_free_bat()`, `setbat()`, `update_bats()`, shared 32-bit KASAN helpers, and linear alias handling. Risks are BAT exhaustion, incorrect clearing of early shadow PTEs, stale BAT/TLB state, and holes in shadow coverage. Test signals include Book3S32 KASAN boot, BAT allocation traces, vmalloc/module shadow tests, and KASAN report generation.
