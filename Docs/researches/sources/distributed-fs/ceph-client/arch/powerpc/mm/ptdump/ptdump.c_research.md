# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/ptdump.c

## Purpose
This file is the generic PowerPC kernel page-table dumper. It traverses `init_mm` page tables, groups contiguous ranges with the same flags and level, prints region markers and decoded attributes to debugfs, and provides a boot/runtime W+X mapping check.

## Important APIs, Types, And Functions
Important types are `struct pg_state` and `struct addr_marker`. Key functions include `pt_dump_size()`, `dump_flag_info()`, `dump_addr()`, `note_prot_wx()`, `note_page_update_state()`, `note_page()`, `populate_markers()`, per-level `note_page_*()` callbacks, `ptdump_show()`, `build_pgtable_complete_mask()`, `ptdump_check_wx()`, and `ptdump_init()`.

## Control Flow
`ptdump_init()` sets the ptdump address range for PPC64, populates marker addresses, computes masks from the selected `pg_level[]` provider, and registers `kernel_page_tables` when debugfs ptdump is enabled. `ptdump_show()` initializes callbacks and calls `ptdump_walk_pgd()`. During walking, `note_page()` starts a range on the first entry and flushes/prints whenever flags, level, or address marker changes. `ptdump_check_wx()` performs the same walk without seq output and counts writable-executable pages.

## State And Persistence
The file maintains static marker and range arrays after init. Per-read state is stack-local. W+X warnings are emitted but no mapping state is changed.

## Dependencies And Integration Points
It depends on generic `linux/ptdump.h`, PowerPC region constants, `pg_level[]` from architecture-specific providers, KASAN/fixmap/vmalloc constants, debugfs, and `init_mm`.

## Risks And Test Signals
Risks include incorrect marker ordering, missing flags in `pg_level[].mask`, false W+X positives/negatives, and PPC64 range start differences between radix and hash. Test signals include debugfs `kernel_page_tables`, `ptdump_check_wx()` during strict RWX boot, KASAN/highmem/fixmap builds, and unknown flag reporting.
