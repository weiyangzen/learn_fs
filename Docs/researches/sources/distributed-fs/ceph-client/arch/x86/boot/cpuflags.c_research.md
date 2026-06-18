# sources/distributed-fs/ceph-client/arch/x86/boot/cpuflags.c

Purpose: gathers CPU feature flags in the minimal boot environment.

Important APIs and state: defines global `struct cpu_features cpu`, `u32 cpu_vendor[3]`, static `loaded_flags`, `cpuid_count()`, `get_cpuflags()`, and 32-bit `has_eflag()`. `has_fpu()` tests FPU availability by clearing CR0 EM/TS, running `fninit`, and checking status/control words.

Control flow: `get_cpuflags()` is idempotent. It records FPU, checks CPUID availability through EFLAGS.ID, reads vendor and basic leaf 1 flags/family/model, leaf 7 subleaf 0 ECX flags into word 16, and extended leaf `0x80000001` flags into words 6 and 1.

Dependencies and integration: supports `cpucheck.c`, TDX detection, and other setup code needing CPUID. Depends on bit operations and early raw assembly only.

Risks and test signals: because `loaded_flags` prevents repeated CPUID loading, feature-fixup code must update `cpu.flags` or deliberately re-probe around it. FPU probing mutates CR0 bits. Test on 32-bit and 64-bit builds, CPUs without CPUID, and feature-specific QEMU models.
