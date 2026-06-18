# sources/distributed-fs/ceph-client/arch/mips/mm/cerr-sb1.c

Purpose: SiByte SB1 cache error decoder and fatal handler. It reads CP0 cache error state, bus watcher state, and cache tag/data contents to print diagnostics before stalling or panicking.

Important APIs/functions: `sb1_cache_error()` is the exception-level C handler. Helpers `breakout_errctl()`, `breakout_cerri()`, `breakout_cerrd()`, `extract_ic()`, `extract_dc()`, `dc_ecc()`, and parity helpers decode I-cache/D-cache tags, data parity, ECC, LRU, and physical/virtual addresses.

Control flow: the handler optionally freezes bus trace, reads CP0 error registers through inline assembly, decodes I-cache and D-cache conditions, validates indicated indexes against EPC/DPA, extracts cache contents when useful, checks bus watcher counters, then either loops forever under `CONFIG_SB1_CERR_STALL` or panics.

State and persistence: no persistent recovery state. It performs destructive reads of bus watcher registers and emits kernel logs.

Dependencies and integration: paired with `cex-sb1.S` low-level vector and selected by R4K cache error setup for SB1 CPUs. Uses SiByte SCD registers and MIPS CP0 cache tag/data registers.

Risks and test signals: must avoid making corruption worse in cache-error context. Test mostly by fault injection/emulation, build configs with/without bus watcher tracing, and validate printed decoding for known tag/ECC patterns.
