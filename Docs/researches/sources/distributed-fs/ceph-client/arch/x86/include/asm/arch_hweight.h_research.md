
# sources/distributed-fs/ceph-client/arch/x86/include/asm/arch_hweight.h

Purpose: architecture-optimized Hamming weight helpers for x86 bit counting.

Important APIs and control flow: `__arch_hweight32()` and 64-bit `__arch_hweight64()` use the alternatives framework to patch from software helpers (`__sw_hweight32`/`__sw_hweight64`) to `popcntl`/`popcntq` when `X86_FEATURE_POPCNT` is present. 16-bit and 8-bit helpers mask and reuse the 32-bit implementation. On 32-bit, 64-bit weight is computed as two 32-bit weights.

State, dependencies, and risks: there is no persistent state; behavior depends on alternative patching and cpufeature detection. Dependencies include `asm/cpufeatures.h`, call constraints, and software fallback symbols. Risks are wrong register constraints across 32/64-bit builds and using POPCNT before alternatives or feature bits are valid. Test signals are bitops/lib tests, compiler build coverage, and runtime CPU feature variation.
