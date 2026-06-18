# sources/distributed-fs/ceph-client/arch/powerpc/lib/mem_64.S

This 64-bit memory helper file exports `memset`, `memmove`, `backwards_memcpy`, and non-KASAN internal helpers `__memset16`, `__memset32`, and `__memset64`. The actual forward `memcpy` symbol lives in `memcpy_64.S` or a feature-routed Power7 variant; `memmove` branches to `memcpy` when the destination is not above the source.

`memset` expands the byte/halfword/word pattern to a 64-bit value, aligns the destination to eight bytes using byte/halfword/word stores, writes 64-byte unrolled blocks, then handles 32/16/8-byte chunks and 4/2/1-byte tails. KASAN wrappers export instrumented aliases. `backwards_memcpy` supports overlapping move when destination is above source: it starts at the end, uses pairs of word loads/stores where possible, aligns backward, and finishes with word/byte tails.

State is only destination memory and registers. Dependencies include PPC64 ABI, KASAN symbol wrappers, and the external forward `memcpy`. Risks are overlap direction mistakes, pattern expansion bugs for `__memset16/32/64`, and alignment assumptions in backwards copy. Test signals include generic string/memory tests, KASAN and non-KASAN builds, `memmove` overlap fuzzing, and boot-time memset-heavy paths.
