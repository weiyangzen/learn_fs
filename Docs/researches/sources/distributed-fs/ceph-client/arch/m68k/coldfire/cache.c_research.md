# sources/distributed-fs/ceph-client/arch/m68k/coldfire/cache.c

Purpose: optional ColdFire data-cache push helper.

When `CACHE_PUSH` is defined, it provides `mcf_cache_push()`, an assembly loop that iterates over cache ways and set offsets and emits the raw opcode word for the ColdFire `cpushl` instruction. It uses `CACHE_LINE_SIZE`, `DCACHE_SIZE`, and `CACHE_WAYS` constants to cover the data cache.

Control flow is a nested assembly loop: clear `d0` for way index, iterate `a0` over lines within each way, execute `cpushl`, increment by cache line size, then advance way count until all ways are pushed.

State affected is CPU cache contents written back to memory. No software state persists.

Dependencies include ColdFire cache geometry macros and assembler compatibility; the raw `.word 0xf468` exists because older GAS versions may not know the mnemonic. Integration is available to low-level cache maintenance callers when `CACHE_PUSH` is configured.

Risks and test signals: wrong geometry constants can miss dirty lines or access invalid cache indices; clobber lists must match assembly use. Test by building with `CACHE_PUSH`, exercising DMA/cache coherency paths, and checking for data corruption around cache writeback-sensitive devices.
