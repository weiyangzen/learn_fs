# sources/distributed-fs/ceph-client/arch/sparc/mm/ultra.S

Purpose: provides SPARC64 low-level TLB/cache flush implementations and SMP cross-call handlers for Spitfire, Cheetah, and sun4v hypervisor systems, with boot-time text patching to select the correct implementation.

Important APIs/functions: public symbols include `__flush_tlb_mm()`, `__flush_tlb_page()`, `__flush_tlb_pending()`, `__flush_tlb_kernel_range()`, `__flush_icache_page()`, optional `__flush_dcache_page()`, SMP handlers `xcall_flush_tlb_mm()`, `xcall_flush_tlb_page()`, `xcall_flush_tlb_kernel_range()`, dcache xcalls, tick/PMU/global-register xcalls, and patchers `cheetah_patch_cachetlbops()` and `hypervisor_patch_cachetlbops()`.

Control flow: generic entry points start as Spitfire demap routines. Cheetah patching replaces fixed instruction windows to use primary context and preserve nucleus page-size fields; hypervisor patching replaces them with fast-trap and unmap-trap calls. Pending/page flushes temporarily install the target context and invalidate D/I MMUs as requested; kernel range flushes demap page-by-page or fall back to full non-locked TLB entry scans/context demap. SMP xcall paths run at trap level and finish with `retry`.

State and persistence: modifies MMU context registers, TLB entries, cache tags, and kernel text instruction sequences. Cross-call snapshot routines write per-CPU diagnostic snapshot arrays.

Dependencies and integration points: used by SPARC64 TLB/cache flush APIs, SMP xcall machinery, hypervisor trap ABI, `tlb.c` batching, dcache alias handling, PMU diagnostics, and tick synchronization.

Risks: instruction counts in patch windows must match callers. PSTATE/TL manipulation, context restore, and hypervisor error handling are correctness-critical. A wrong demap scope can either miss stale translations or evict locked kernel mappings.

Test signals: boot Spitfire, Cheetah, and sun4v systems; run SMP TLB shootdown stress, BPF/JIT text flushes, kernel module load/unload, dcache alias tests, hypervisor trap failure injection, PMU snapshot users, and tick synchronization.
