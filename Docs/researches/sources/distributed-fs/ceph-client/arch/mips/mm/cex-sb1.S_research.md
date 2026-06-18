# sources/distributed-fs/ceph-client/arch/mips/mm/cex-sb1.S

Purpose: SB1-specific cache error vector with limited recovery for certain I-cache errors and fatal dispatch for unrecoverable cases.

Important symbols: `except_vec2_sb1` is copied to the vector; `handle_vec2_sb1` switches KSEG0 uncached, obtains a usable stack if possible, and jumps to `sb1_cache_error()`.

Control flow: the vector saves `k0/k1` to low memory, checks `C0_ERRCTL` recoverable and cache-type bits, treats D-cache and unclear cases as unrecoverable, invalidates all ways for recoverable internal I-cache errors at the indicated index, restores scratch regs and `eret`s. Fatal path disables caching and jumps to the C decoder.

State and persistence: temporarily uses low memory locations `0x170/0x178`, mutates cache tags via `cache Index_Invalidate_I`, and changes CP0 Config on fatal path.

Dependencies and integration: installed by `r4k_cache_error_setup()` for SB1/SB1A and paired with `cerr-sb1.c`.

Risks and test signals: low-memory scratch use can race across CPUs; vector instruction budget is strict. Test recoverable icache injection, fatal dcache path, SMP reentry assumptions, and config options forcing fatal behavior.
