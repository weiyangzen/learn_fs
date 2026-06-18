# sources/distributed-fs/ceph-client/arch/powerpc/lib/hweight_64.S

This file exports optimized 64-bit PowerPC population-count helpers: `__arch_hweight8`, `__arch_hweight16`, `__arch_hweight32`, and `__arch_hweight64`. Each returns the number of set bits in the low 8, 16, 32, or 64 bits of `r3`.

Each function is wrapped in feature-fixup sections. If `CPU_FTR_POPCNTB` is missing, the code branches to generic software helpers such as `__sw_hweight32`. If byte popcount exists but doubleword popcount does not, wider functions use `PPC_POPCNTB` plus shifts and adds to aggregate byte counts. If `CPU_FTR_POPCNTD` exists, 16/32/64-bit paths use word or doubleword popcount directly and mask down to the final byte result. Nested feature sections select the best available instruction while keeping a valid fallback layout.

There is no persistent state. Dependencies include `asm/feature-fixups.h`, `PPC_POPCNT*` opcode macros, software hweight helpers, and the kernel bitops API. Risks are wrong feature selection, accidentally counting high unused bits for narrower helpers, and macro layout breakage under `-mminimal-toc`. Test signals include lib/bitmap and hweight tests, boot on CPUs with/without popcount instructions, and comparing arch helpers to software helpers for randomized values.
