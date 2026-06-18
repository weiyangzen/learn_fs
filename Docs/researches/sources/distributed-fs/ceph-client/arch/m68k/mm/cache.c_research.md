# sources/distributed-fs/ceph-client/arch/m68k/mm/cache.c

## Purpose
Implements m68k instruction-cache flushing for user ranges, kernel ranges, and individual user pages across ColdFire, 68040/060, and older CACR-based CPUs.

## APIs, Flow, And State
`virt_to_phys_slow()` translates virtual addresses for 040/060 cache push operations: 060 uses `plpar` with exception-table fixup returning zero on translation failure; 040 uses `ptestr` and `mmusr`. `flush_icache_user_range()` handles ColdFire set-index flushing with wraparound, 040/060 page-by-page `cpushp %bc` using translated physical addresses, or older `cacr` instruction-cache flush. `flush_icache_range()` temporarily switches function code to supervisor data, flushes, restores user data, and is exported. `flush_icache_user_page()` flushes one page using the same CPU-family split.

## Dependencies And Integration
Depends on `asm/cacheflush.h`, `asm/traps.h`, CPU feature macros, ColdFire cache helpers, page structures, exception tables, and function-code helpers. Used by text modification, module loading, signal trampolines, and user-page executable updates.

## Risks And Test Signals
The slow translation path can produce physical zero on failure, so callers should operate on valid mappings. ColdFire set-mask wrap logic and 040/060 physical cache pushes are CPU-specific. Test signals include module load/execute, signal trampoline execution, self-modifying/JIT-style user code, and cache-flush behavior on ColdFire, 040, 060, and older m68k CPUs.
