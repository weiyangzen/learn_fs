# sources/distributed-fs/ceph-client/arch/powerpc/mm/ptdump/shared.c

## Purpose
This file defines a shared ptdump flag table for several non-Book3S64 PowerPC MMU configurations, including 44x, e500, and Book3S32. It supplies the generic walker with readable names for common PTE bits.

## Important APIs, Types, And Functions
The important data is `flag_array[]` and exported `pg_level[5]`. Flags cover read, write, execute, present, coherent, guarded, dirty, accessed, write-through, no-cache, and special states.

## Control Flow
There is no active control flow. `ptdump.c` reads the static descriptors when grouping and printing page-table ranges.

## State And Persistence
The static `pg_level[]` table persists for the lifetime of the kernel. It does not mutate page tables.

## Dependencies And Integration Points
It depends on common PowerPC PTE bit definitions and `ptdump.h`. The Makefile selects it for 44x, PPC_E500, and PPC_BOOK3S_32.

## Risks And Test Signals
Risks include shared labels being too generic for one MMU family and incorrect unknown-bit masking. Test signals include debugfs ptdump output on 44x/e500/Book3S32, strict W+X checks, and build coverage for each selected configuration.
