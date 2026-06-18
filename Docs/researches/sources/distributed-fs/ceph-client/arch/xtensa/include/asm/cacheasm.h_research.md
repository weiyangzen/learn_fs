<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheasm.h -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheasm.h

## Purpose
Defines assembly macros for Xtensa cache maintenance: invalidate, flush, and flush-invalidate operations over all cache, pages, or address ranges.

## Important APIs, Types, And Functions
Macros include low-level variants such as `___invalidate_icache_all`, `___invalidate_dcache_all`, `___flush_dcache_all`, `___flush_invalidate_dcache_all`, page/range operations, and feature-conditional cache instruction sequences.

## Control Flow
Macros expand to loops over cache ways/sets or address ranges using Xtensa cache instructions selected by core cache features. They often rely on loop helpers from `asmmacro.h` and are used before executing relocated code or after modifying memory visible to instruction fetch.

## State And Persistence
They mutate CPU cache state only. No persistent software state is owned.

## Dependencies And Integration Points
Depends on variant cache geometry, Xtensa cache instruction availability, and assembly users in boot, cacheflush implementation, and low-level memory code.

## Risks And Edge Cases
Wrong way/set iteration or missing `isync`/ordering can execute stale code or lose dirty data. Writeback versus non-writeback cache variants require different behavior. Range alignment must cover entire cache lines.

## Test Signals
Boot compressed images, run self-modifying/ftrace/module code paths, execute cache aliasing tests, and test variants with writeback and non-writeback caches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/asm/cacheasm.h -->
