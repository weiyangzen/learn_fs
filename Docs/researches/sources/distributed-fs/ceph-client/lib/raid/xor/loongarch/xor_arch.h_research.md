# sources/distributed-fs/ceph-client/lib/raid/xor/loongarch/xor_arch.h

Purpose: registers LoongArch XOR implementations, including generic fallbacks and LSX/LASX SIMD candidates.

Important APIs and flow: `arch_xor_init()` always registers `8regs`, `8regs_prefetch`, `32regs`, and `32regs_prefetch`. It conditionally registers `xor_block_lsx` and `xor_block_lasx` when build options and runtime CPU feature flags are available.

State and persistence: no persistent state beyond the core's init-time template list and measured speeds.

Dependencies and integration: depends on `<asm/cpu-features.h>` and templates from `xor_simd_glue.c`.

Risks and test signals: vector templates intentionally participate in calibration instead of being forced because future LoongArch cores may vary. Signals include boot speed comparison, LSX/LASX feature detection, and KUnit parity checks.
