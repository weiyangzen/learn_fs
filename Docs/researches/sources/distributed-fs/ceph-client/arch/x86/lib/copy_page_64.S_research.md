# sources/distributed-fs/ceph-client/arch/x86/lib/copy_page_64.S

Purpose: implements the 64-bit `copy_page` primitive for copying one 4 KiB page.

Important APIs/functions: exports `copy_page`. Internal `copy_page_regs` is an unrolled register-copy fallback. `ALTERNATIVE` selects the fast `rep movsq` implementation when `X86_FEATURE_REP_GOOD` is available.

Control flow: on CPUs with good REP behavior, the function copies `4096/8` quadwords with `rep movsq`. Otherwise it saves `%rbx` and `%r12`, copies 64-byte chunks with eight general-purpose registers and prefetching, then copies a final fixed five chunks, restores registers, and returns.

State and persistence behavior: writes exactly one page at the destination from the source page. No global state.

Dependencies/integration points: used by memory-management page copy paths. Depends on x86 alternatives, CPU feature detection, Linux export/linkage, and the calling convention where `%rdi` and `%rsi` are destination/source.

Risks: assumes caller provides valid page-sized source/destination. Register save/restore correctness matters because fallback clobbers callee-saved registers. Alternative patching must match CPU feature semantics.

Test signals: boot-time page allocator and fork/COW behavior, memory copy stress, alternative instruction patching tests, and objtool/build validation.
