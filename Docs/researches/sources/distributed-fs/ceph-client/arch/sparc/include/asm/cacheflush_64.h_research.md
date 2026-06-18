<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_64.h -->
# sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_64.h

## Purpose
This header defines SPARC64 cache and instruction-flush interfaces.

## Important APIs, Types, and Functions
It declares/defines `flush_cache_*`, `flush_icache_range`, page/folio dcache flush hooks, user-page copy helpers, and SPARC64-specific flush routines used by MM and text modification.

## Control Flow
Generic MM calls these hooks when mappings change, pages are copied, executable memory is updated, or vmalloc areas are created/removed.

## State and Persistence Behavior
Operations mutate hardware cache state only. No persistent header-owned state exists.

## Dependencies and Integration Points
It integrates with SPARC64 MMU/cache code, executable mappings, module loading, BPF/ftrace text patching, and DMA coherency.

## Risks
Instruction/data cache coherency is critical for text patching and user executable mappings. Incomplete flushing causes stale instruction execution.

## Test Signals
Run module load/unload, ftrace/BPF text modification, JIT/self-modifying code tests, and mmap executable write/execute coherency checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/asm/cacheflush_64.h -->
