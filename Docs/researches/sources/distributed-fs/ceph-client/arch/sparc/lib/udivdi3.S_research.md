# sources/distributed-fs/ceph-client/arch/sparc/lib/udivdi3.S

Purpose: GNU CC runtime helper `__udivdi3` implementing unsigned 64-bit division on SPARC using 32-bit operations and hand-inlined long division primitives.

Important APIs/functions: `__udivdi3` accepts numerator/divisor halves by SPARC ABI and returns a 64-bit quotient. The file embeds repeated `udiv_qrnnd`-style loops and one `umul_ppmm` verification/correction sequence. It references `__clz_tab` for normalization shift calculation.

Control flow: the routine distinguishes divisor high word zero from nonzero. For single-word divisors it performs one or two 32-bit quotient/remainder divisions, including an intentional hardware divide-by-zero path when divisor is zero. For multiword divisors it normalizes using leading-zero count, divides the normalized high words, multiplies the tentative quotient by the divisor low word, and decrements the quotient when the product is too large. It returns quotient high/low via locals restored into outputs.

State and persistence: no persistent state. Uses `%y`, stack frame, condition codes, and local registers. It does not write memory.

Dependencies/integration: depends on `__clz_tab` supplied by the kernel/libgcc support set. Used when compiler-generated unsigned long-long division cannot be inlined.

Risks: division helpers are high-risk because rare boundary combinations trigger correction paths. Divide-by-zero behavior intentionally traps via `udiv`; replacing it with a silent branch would alter ABI semantics. Normalization assumes `__clz_tab` availability and correct byte selection.

Test signals: exhaustive-ish randomized unsigned 64-bit division against C reference; boundary divisors 0, 1, 2^32-1, 2^32, high-word-only divisors, numerator < divisor, numerator == divisor, and quotient correction cases. Link tests should confirm `__clz_tab` resolves.
