<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_no.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_no.h

## Purpose
This header implements cache maintenance for non-MMU m68k/ColdFire systems. It provides whole-cache and range-compatible hooks backed by ColdFire CACR operations and optional `mcf_cache_push()`.

## Important APIs, Types, And Functions
- `flush_cache_all()`, `flush_dcache_range()`, and `flush_icache_range()` map to whole-cache helpers.
- `mcf_cache_push()` is an external writeback helper.
- `__clear_cache_all()`, `__flush_cache_all()`, `__flush_icache_all()`, and `__flush_dcache_all()` manipulate CACR invalidation/push constants.
- `cache_push()` and `cache_clear()` ignore ranges and flush/clear globally.
- Includes `asm-generic/cacheflush.h` for remaining hooks.

## Control Flow
Compile-time cache constants determine whether assembly writes to `CACR` are emitted. Data-cache flush optionally pushes dirty lines first, then invalidates. Range APIs fall back to whole-cache operations because the hardware may not support precise line operations.

## State And Persistence Behavior
The only affected state is CPU cache/write-buffer state. No software state is stored by the header.

## Dependencies And Integration Points
It depends on ColdFire `mcfsim.h`, cache configuration constants, Linux MM types, and generic cacheflush definitions. It integrates with non-MMU executable loading, DMA, and memory update paths.

## Risks And Edge Cases
Range arguments are ignored, which is correct but potentially expensive. Missing `CACHE_PUSH` support risks discarding dirty data if invalidation is used without writeback. CACR constants must match the ColdFire variant.

## Test Signals
Non-MMU ColdFire boot, executable load after writes, DMA coherency, cache-disabled configs, and builds with separate instruction/data cache constants validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/cacheflush_no.h -->
