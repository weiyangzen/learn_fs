# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/8xx.c

## Purpose
This file supplies the page-table dump flag descriptions for PPC 8xx. It does not walk page tables itself; it defines how generic `ptdump.c` should decode 8xx PTE bits at each level.

## Important APIs, Types, And Functions
The key data is `flag_array[]` and exported `pg_level[5]`. Entries describe huge-page flags (`_PAGE_HUGE` or `_PAGE_SPS` depending on page size), read/write/NA combinations, execute, present, guarded, dirty, accessed, no-cache, and special bits.

## Control Flow
At runtime `ptdump.c` consults `pg_level[level].flag`, `.num`, and a computed `.mask` to group and print page-table ranges. This file's only active behavior is static initialization of those decode tables.

## State And Persistence
The decode table is static kernel data and persists for the lifetime of the debug page-table dump facility. It does not modify MMU state.

## Dependencies And Integration Points
It depends on 8xx page-bit definitions from `linux/pgtable.h` and the shared `ptdump.h` structure layout. It is selected by the ptdump Makefile under `CONFIG_PPC_8xx`.

## Risks And Test Signals
Risks are stale or incorrect flag names/masks leading to misleading debugfs output and W+X checks masking unknown bits incorrectly. Test signals include reading `/sys/kernel/debug/kernel_page_tables` on 8xx, verifying huge-page labels under 16K and non-16K builds, and checking unknown flag reporting.
