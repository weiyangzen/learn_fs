# sources/distributed-fs/ceph-client/arch/x86/kernel/cpu/centaur.c

## Purpose
`centaur.c` provides the x86 vendor driver for Centaur/VIA/Zhaoxin-style CPUs identified by `CentaurHauls`. It performs early feature normalization, enables legacy VIA/Centaur crypto and RNG units, handles old 32-bit WinChip/C3 quirks, fixes cache reporting, and registers the vendor with the generic CPU identification framework.

## Important APIs, Types, and Functions
The central registered object is `centaur_cpu_dev`, with `c_early_init = early_init_centaur`, `c_init = init_centaur`, optional 32-bit `legacy_cache_size = centaur_size_cache`, and `c_x86_vendor = X86_VENDOR_CENTAUR`.

`early_init_centaur()` sets `X86_FEATURE_CENTAUR_MCR` on family 5 32-bit systems, marks constant/nonstop TSC based on family/model and `x86_power`, and runs before full vendor init. `init_centaur()` calls `init_intel_cacheinfo()`, detects architectural perfmon, handles family 5 FCR/model-name setup on 32-bit, calls `init_c3()` for family 6+ units, forces `LFENCE_RDTSC` on 64-bit, and finishes with `init_ia32_feat_ctl()`. `init_c3()` enables ACE crypto and RNG via VIA MSRs and sets feature bits.

## Control Flow
`cpu_dev_register(centaur_cpu_dev)` places the descriptor in the `.x86_cpu_dev.init` section. `common.c` discovers it in `init_cpu_devs()`, matches `CentaurHauls`, runs early init during early boot, and later runs full init from `identify_cpu()`. Cache reporting uses Intel paths because these CPUs expose compatible cache leaves/descriptors.

On 32-bit family 5, `init_centaur()` rewrites FCR bits for specific WinChip models, may clear broken TSC, sets Centaur MCR/CX8/3DNow capabilities, reads extended cache leaves when present, and builds a model string. On C3-family systems it enables ACE/RNG if the extended Centaur CPUID leaf reports units present but disabled.

## State and Persistence
State is mainly in `struct cpuinfo_x86` feature, cache, and model fields. MSR writes to VIA FCR/RNG registers persist for the running CPU. Feature corrections are not stored outside CPU caps but become part of the boot CPU common capability set and per-CPU state.

## Dependencies and Integration Points
The file depends on x86 CPUID helpers, MSR helpers, MTRR, E820, scheduler clock headers, and generic `cpu.h` vendor registration. It integrates with `common.c` CPU identification and with `cacheinfo.c` through `init_intel_cacheinfo()`.

## Risks
Much of the 32-bit logic touches old model-specific FCR bits; incorrect model matching could expose broken TSC or wrong cache sizes. ACE/RNG enablement assumes VIA extended CPUID/MSRs behave as expected. The code is low churn but covers rare hardware, so regressions are likely to be found only by boot testing on affected systems or emulation.

## Test Signals
Boot on Centaur/VIA/Zhaoxin hardware or targeted emulation and check CPU vendor/model, feature flags for ACE/RNG/CX8/3DNow/REP_GOOD/constant TSC, cacheinfo output, and dmesg lines for ACE/RNG enablement or FCR changes. On old 32-bit models, verify TSC stability decisions and `centaur_size_cache()` corrections.
