# sources/distributed-fs/ceph-client/arch/mips/mm/cex-oct.S

Purpose: Octeon-specific cache error exception vector. It captures dcache error state before memory access and dispatches recoverable or nonrecoverable errors.

Important symbols: `except_vec2_octeon` is the compact vector; `handle_cache_err` saves full exception state and calls `cache_parity_error_octeon_recoverable()`.

Control flow: reads hardware core id, indexes `cache_err_dcache`, reads and clears CP0 Dcache CacheErr before normal memory activity, checks EXL for nested exception, jumps directly to nonrecoverable panic path if nested, otherwise saves registers and returns through `ret_from_exception` after the C handler.

State and persistence: writes captured dcache error to global `cache_err_dcache[core]` for later reporting.

Dependencies and integration: installed by `octeon_cache_error_setup()` in `c-octeon.c`; depends on Octeon CP0 selectors, stackframe macros, and C handlers.

Risks and test signals: ordering before memory access is essential due to errata. Test vector size, nested exception path, recoverable return, per-core storage, and correct clearing of CacheErr.
