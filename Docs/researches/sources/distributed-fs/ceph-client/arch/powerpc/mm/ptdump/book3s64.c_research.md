# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/book3s64.c

## Purpose
This file defines Book3S64 page-table flag decoding for the generic ptdump walker. It maps Linux PTE and hash-specific bits into readable labels for debugfs page-table dumps and W+X checking.

## Important APIs, Types, And Functions
The primary data structures are `flag_array[]` and exported `pg_level[5]`. Flags include user/privileged, read, write, execute, leaf PTE, valid/present, hash PTE state, dirty/accessed, non-idempotent/tolerant cache attributes, busy, 64K combo or 4K PFN state, f_gix/f_second for non-64K pages, and special.

## Control Flow
There is no executable control path beyond static data initialization. `ptdump.c` later computes per-level masks from this table and uses it to group and print page-table ranges.

## State And Persistence
The flag tables are persistent read-only kernel data. They do not mutate page tables.

## Dependencies And Integration Points
This file depends on Book3S64 PTE/hash bit definitions and the shared `ptdump.h` ABI. It is selected by the ptdump Makefile for `CONFIG_PPC_BOOK3S_64`.

## Risks And Test Signals
Risks include misleading diagnostics if bit definitions drift, especially around hash HPTE status and 64K subpage encodings. Test signals include debugfs `kernel_page_tables` output on radix and hash Book3S64, 64K and non-64K page configurations, and W+X check output containing no unknown expected bits.
