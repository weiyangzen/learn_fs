# sources/distributed-fs/ceph-client/lib/raid/xor/powerpc/xor_arch.h

Purpose: registers PowerPC XOR templates, including generic fallbacks and optional AltiVec.

Important APIs and flow: `arch_xor_init()` registers all four generic scalar templates. With `CONFIG_ALTIVEC` and `CPU_FTR_ALTIVEC`, it also registers `xor_block_altivec` for calibration.

State and persistence: no persistent state beyond the XOR core's template list and selected static call target.

Dependencies and integration: depends on `<asm/cpu_has_feature.h>` and the VMX glue template.

Risks and test signals: risk is CPU feature detection or SIMD-state management in the selected AltiVec path. Signals include boot measurement logs, KUnit, and RAID5 parity workloads on PowerPC AltiVec systems.
