# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/cpuid-deps.c

## Purpose
`cpuid-deps.c` enforces dependency relationships between x86 CPU feature bits. When a feature is cleared by command line, config, erratum handling, microcode state, or generic filtering, dependent features are recursively cleared so the final capability set does not advertise impossible or unsafe combinations.

## Important APIs, Types, and Functions
`struct cpuid_dep` maps a feature to the feature it depends on. `cpuid_deps[]` covers FPU/FXSR, XSAVE families, vector extensions, AVX512 subfeatures, resource-control subfeatures, SGX subfeatures, AMX/XFD, shadow stack, FRED/LKGS, SSBD/SPEC_CTRL, and LASS/SMAP.

Public APIs are `clear_cpu_cap(struct cpuinfo_x86 *c, unsigned int feature)`, `setup_clear_cpu_cap(unsigned int feature)`, and `check_cpufeature_deps(struct cpuinfo_x86 *c)`. Internals include `clear_feature()`, `do_clear_cpu_cap()`, and `x86_feature_name()`.

## Control Flow
`do_clear_cpu_cap()` first clears the requested feature on either a specific CPU or the boot CPU/global cleared bitmap, warns if clearing an already-boot-visible feature after alternatives were patched, then builds a bitmap of disabled features. It repeatedly scans `cpuid_deps[]` until no newly dependent features are added, clearing each dependent capability as it goes.

`check_cpufeature_deps()` is a diagnostic pass used after feature discovery/filtering. It warns once if a CPU still has a feature set while its dependency is absent.

## State and Persistence
For boot-global clearing, `clear_feature(NULL, feature)` mutates `boot_cpu_data` and records the bit in `cpu_caps_cleared` so later CPUID probes and APs inherit the forced clear. Per-CPU clearing mutates only that CPU's `x86_capability`. There is no persistent storage beyond the capability bitmaps.

## Dependencies and Integration Points
The file depends on `asm/cpufeature.h`, `boot_cpu_data`, `alternatives_patched`, feature-name arrays, and the global forced-cap bitmaps declared in `common.c`. `common.c` calls dependency checks during early and full identification, and feature clearing is used throughout CPU/vendor/mitigation code.

## Risks
The dependency table is policy-sensitive: missing entries can leave impossible CPUID combinations, while overly broad dependencies can hide usable features. Clearing after alternatives are patched may not update patched code paths, hence the warning. The recursive algorithm assumes dependency count is small and acyclic enough to converge quickly.

## Test Signals
Boot with `clearcpuid=` for base features such as `xsave`, `avx`, `avx512f`, `sgx`, `xfd`, or `smap` and verify dependent flags disappear from `/proc/cpuinfo`. Check dmesg for dependency warnings on deliberately inconsistent virtual CPUID. Build/run CPU hotplug because the table is not `__init`.
