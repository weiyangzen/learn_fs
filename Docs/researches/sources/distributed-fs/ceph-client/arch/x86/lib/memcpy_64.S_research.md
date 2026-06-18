# sources/distributed-fs/ceph-client/arch/x86/lib/memcpy_64.S

Purpose: implements 64-bit `memcpy`/`__memcpy` in noinstr text with alternatives for fast short `rep movsb` and an optimized manual fallback.

Important APIs/functions: exports `__memcpy` and aliases/exports `memcpy`. Local `memcpy_orig` handles the fallback path.

Control flow: if `X86_FEATURE_FSRM` is available, `__memcpy` copies with `rep movsb` after moving destination to `%rax` for return. Otherwise it jumps to `memcpy_orig`, which copies 32-byte chunks forward or backward depending on low-byte ordering to reduce false dependencies, then handles 16-, 8-, 4-, and 1-3-byte tails using overlapping loads/stores.

State and persistence behavior: copies bytes from source to destination and returns original destination. No global state. Although `memcpy` has no overlap guarantee, the fallback contains backward-copy handling for dependency/performance considerations.

Dependencies/integration points: core kernel memory operations, x86 alternative patching, CFI type annotations, noinstr constraints, and exported module symbols.

Risks: being in `.noinstr.text` forbids instrumentation. Tail copy patterns use overlapping loads/stores and require valid ranges. Alternative patching and return-value preservation are ABI-critical.

Test signals: memcopy correctness tests for all small sizes/alignment combinations, large-copy performance/correctness tests, FSRM and non-FSRM CPU coverage, objtool noinstr validation, and KASAN/KMSAN builds.
