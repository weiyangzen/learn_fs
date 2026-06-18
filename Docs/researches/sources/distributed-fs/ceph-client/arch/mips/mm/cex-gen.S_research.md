# sources/distributed-fs/ceph-client/arch/mips/mm/cex-gen.S

Purpose: generic MIPS cache error exception vector used when no CPU-specific vector is installed.

Important symbols: `except_vec2_generic` is copied to the cache error vector. It disables KSEG0 caching by clearing cache mode bits in CP0 Config and setting uncached mode, waits a few cycles, then jumps to `cache_parity_error`.

Control flow: runs in a highly constrained exception context with `noreorder`, `noat`, and minimal instructions. It does not save full register state; it uses `k0/k1` scratch registers and transfers to the secondary C/assembly error path.

State and persistence: mutates CP0 Config cache coherency mode. No memory state is allocated.

Dependencies and integration: installed by `r4k_cache_error_setup()` for non-SB1 CPUs. Depends on `cache_parity_error` existing elsewhere in the MIPS exception code.

Risks and test signals: vector size and instruction safety are critical because caches may be unreliable. Test by build/link checks, vector copy size validation, and cache error injection where available.
