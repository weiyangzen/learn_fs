# sources/distributed-fs/ceph-client/arch/microblaze/kernel/cpu/cache.c

Purpose: implements MicroBlaze cache enable/disable, invalidate, and flush operations selected at boot from the probed/static CPU description. It provides the `mbc` `struct scache` dispatch table consumed by cacheflush helpers, then `microblaze_cache_init()` binds it to write-back/write-through and MSR-instruction/no-MSR variants.

Important APIs and state: low-level inline MSR helpers toggle `MSR_ICE` and `MSR_DCE`; cache loops issue `wic`, `wdc`, `wdc.flush`, and `wdc.clear`; `mbc` is exported through `microblaze_ksyms.c`. The implementation depends on `cpuinfo` sizes, line lengths, `dcache_wb`, `ver_code`, and `PVR2_USE_MSR_INSTR`.

Control flow: range helpers align/limit addresses to one cache footprint, optionally disable interrupts/cache for older write-through paths, loop by cache line, then restore cache/MSR state. Whole-cache helpers sweep `cpuinfo.*cache_size`. `microblaze_cache_init()` chooses one of six static `scache` tables, warns about old write-back hardware, enables dcache, invalidates icache, and enables icache.

State and persistence: persistent state is the global `mbc` function table plus CPU MSR cache bits. No dynamic allocation occurs. Cache operations have hardware-visible side effects and must preserve interrupt and virtual-mode assumptions.

Dependencies and integration: used by DMA, module finalization, ftrace patching, signal trampolines, kgdb, and coherent allocation paths. It relies on correct PVR/DTS data from the CPU-info files.

Risks and test signals: wrong line size or cache mode can lose dirty data or leave stale instructions after text patching. Old write-through paths intentionally disable cache/IRQs. Build and boot with MSR/non-MSR, write-back/write-through configurations; exercise module loading, dynamic ftrace, signal return trampolines, DMA sync, and cache debug prints.
