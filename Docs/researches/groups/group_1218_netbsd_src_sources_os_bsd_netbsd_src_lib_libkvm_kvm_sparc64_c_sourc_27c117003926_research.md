# Group Research: group_1218_netbsd_src_sources_os_bsd_netbsd_src_lib_libkvm_kvm_sparc64_c_sourc_27c117003926

Scope: `Docs/research_subset_a.md` (`sources/os/bsd/netbsd-src`). All 167 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc64.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc64.c
SPARC64 `libkvm` crash-dump backend. It translates kernel virtual addresses through SPARC64 kcore metadata, wired 4 MB mappings, per-CPU mappings, legacy text/data ranges, and page-table TTEs, then maps physical RAM segments to dump offsets. Read: 280 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sparc64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun2.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun2.c
Sun2 m68k `libkvm` operations backend. It uses dumped Sun2 segment-map/PMEG state to translate kernel virtual addresses and maps physical addresses directly to dump offsets. Read: 181 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun2.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3.c
Sun3 m68k `libkvm` operations backend. It reads Sun3 kcore MMU state, resolves segment-map entries to PMEG PTEs, validates pages, and returns contiguous bytes within the translated page. Read: 181 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3x.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3x.c
Sun3x m68k `libkvm` backend. It handles the contiguous kernel mapping directly, otherwise reads kernel PTEs via `kvm_read`, and converts sparse RAM segments into packed dump offsets. Read: 176 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_sun3x.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_vax.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_vax.c
Minimal VAX `libkvm` backend, described in-file as effectively an error-stub. It records `_end`, accepts kernel addresses between `KERNBASE` and `_end`, and linearly maps them to physical/dump offsets. Read: 157 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_vax.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_x86_64.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libkvm/kvm_x86_64.c
x86-64 `libkvm` crash-dump backend. It walks level-4 through level-1 page tables, supports 1 GiB and 2 MiB large pages, and lazily builds a physical-address-to-dump-offset map from kcore RAM segments. Read: 276 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libkvm/kvm_x86_64.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/Makefile
Top-level NetBSD `libm` build recipe. It selects architecture-specific math/fenv sources, substitutes assembly overrides for generic C implementations, merges export-symbol lists, adds softfloat fenv stubs when needed, and defines installed math manual links. Read: 586 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrt.S
AArch64 double `__ieee754_sqrt` implementation using `fsqrt d0, d0`. Read: 39 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrtf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrtf.S
AArch64 float `__ieee754_sqrtf` implementation using `fsqrt s0, s0`. Read: 39 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/e_sqrtf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/fenv.c
AArch64 ISO C fenv implementation. It reads/writes FPCR and FPSR for exception flags, masks, rounding mode, environment save/restore, hold, update, and trap-enable queries. Read: 257 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fabsf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fabsf.S
AArch64 `fabsf` implementation using the scalar FP absolute-value instruction. Read: 39 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fabsf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fma.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fma.S
AArch64 double `fma`/`_fma` implementation using `fmadd d0, d0, d1, d2`. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fma.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaf.S
AArch64 float `fmaf`/`_fmaf` implementation using `fmadd s0, s0, s1, s2`. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmax.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmax.S
AArch64 double `fmax`/`_fmax` implementation using native scalar FP maximum. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmax.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaxf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaxf.S
AArch64 float `fmaxf`/`_fmaxf` implementation using native scalar FP maximum. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmaxf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmin.S
AArch64 double `fmin`/`_fmin` implementation using native scalar FP minimum. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fmin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fminf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fminf.S
AArch64 float `fminf`/`_fminf` implementation using native scalar FP minimum. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/aarch64/s_fminf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/fenv.c
Alpha fenv support for environment save/restore and trap enable state. It uses `ieee_get_fp_control` and `ieee_set_fp_control`; several flag/rounding routines are supplied inline by Alpha `fenv.h`. Read: 149 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/lrint.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/lrint.S
Alpha `lrint` assembly conversion routine for rounding a floating-point value to integer. Read: 21 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/lrint.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysign.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysign.S
Alpha double/long-double `copysign` implementation with aliases between `copysign`, `_copysignl`, and `copysignl`. Read: 40 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysign.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysignf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysignf.S
Alpha float `copysignf` implementation using sign-bit manipulation. Read: 37 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/alpha/s_copysignf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/e_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/e_sqrt.S
ARM VFP double `__ieee754_sqrt` implementation using `vsqrt.f64`. Read: 39 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/e_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/e_sqrtf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/e_sqrtf.S
ARM VFP float `__ieee754_sqrtf` implementation using `vsqrt.f32`. Read: 39 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/e_sqrtf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/fenv.c
ARM VFP fenv implementation. It manipulates FPSCR exception flags, masks, rounding mode, saved environments, hold/update behavior, and enabled exceptions. Read: 263 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrint.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrint.S
ARM VFP `lrint`/`lrintl` assembly conversion routine with weak/strong aliases around `_lrint`. Read: 42 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrint.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrintf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrintf.S
ARM VFP `lrintf` assembly conversion routine aliased through `_lrintf`. Read: 40 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/lrintf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fabsf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fabsf.S
ARM VFP `fabsf` implementation. Read: 37 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fabsf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fma.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fma.S
ARM VFP double `fma`/`fmal` assembly implementation using fused multiply-add support and aliases. Read: 42 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fma.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fmaf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fmaf.S
ARM VFP float `fmaf` assembly implementation. Read: 40 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/arm/s_fmaf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/hppa/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/hppa/fenv.c
HPPA fenv implementation. It reads/writes FPSR fields for exception flags, rounding mode, saved environments, hold/update behavior, and enabled exception masks. Read: 369 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/hppa/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/Makefile
Small i387 subdirectory makefile that includes NetBSD build framework files; actual i387 source selection is controlled by the parent `libm/Makefile`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/abi.h -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/abi.h
ABI helper header for i387 assembly. It abstracts i386 vs x86_64 argument locations, return conventions, PIC data access, and temporary stack/control-word storage. Read: 81 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/abi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_acos.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_acos.S
i387 `__ieee754_acos` implementation using x87 stack operations, square root, absolute value handling, and atan-style reduction. Read: 25 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_acos.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_asin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_asin.S
i387 `__ieee754_asin` implementation using x87 stack operations and square-root reduction. Read: 23 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_asin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2.S
i387 double `__ieee754_atan2` implementation using x87 `fpatan`-style argument loading. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2f.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2f.S
i387 float `__ieee754_atan2f` implementation using x87 float argument loading. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_atan2f.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_exp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_exp.S
i387 double `__ieee754_exp` implementation using x87 `fldl2e`, `frndint`, `f2xm1`, and `fscale`, with special-case handling for infinities. Read: 108 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_exp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_expf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_expf.S
i387 float `__ieee754_expf` implementation using x87 exponent decomposition and scaling. Read: 55 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_expf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_fmod.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_fmod.S
i387 double `__ieee754_fmod` implementation using repeated x87 `fprem`. Read: 23 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_fmod.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log.S
i387 double `__ieee754_log` implementation using `fldln2` and `fyl2x`. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log10.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log10.S
i387 double `__ieee754_log10` implementation using `fldlg2` and `fyl2x`. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log10.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log10f.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log10f.S
i387 float `__ieee754_log10f` implementation using x87 log-base conversion. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log10f.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log2.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log2.S
i387 double `__ieee754_log2` implementation using `fld1` and `fyl2x`. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log2.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log2f.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log2f.S
i387 float `__ieee754_log2f` implementation using x87 base-2 logarithm support. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_log2f.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_logf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_logf.S
i387 float `__ieee754_logf` implementation using `fldln2` and `fyl2x`. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_logf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainder.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainder.S
i387 double `__ieee754_remainder` implementation using repeated x87 `fprem1`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainder.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainderf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainderf.S
i387 float `__ieee754_remainderf` implementation using repeated x87 `fprem1`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_remainderf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalb.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalb.S
i387 double `__ieee754_scalb` implementation using x87 `fscale`. Read: 19 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalb.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalbf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalbf.S
i387 float `__ieee754_scalbf` implementation using x87 `fscale`. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_scalbf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrt.S
i387 double `__ieee754_sqrt` implementation using x87/SSE square-root instructions depending on target mode. Read: 17 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrtf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrtf.S
i387 float `__ieee754_sqrtf` implementation using x87/SSE square-root instructions depending on target mode. Read: 17 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/e_sqrtf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/empty.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/empty.S
Intentionally empty assembly placeholder containing only a newline. Read: 1 line.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/empty.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/fenv.c
i387/SSE fenv implementation. It coordinates x87 control/status words with SSE MXCSR, detects SSE availability in `__init_libm`, and implements exception flags, masks, rounding, hold, restore, update, and trap controls. Read: 534 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/lrint.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/lrint.S
i387 `lrint` assembly routine converting a loaded double to integer according to FP rounding behavior. Read: 23 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/lrint.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atan.S
i387 double `atan`/`_atan` implementation using x87 argument setup and atan instruction sequence. Read: 23 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atanf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atanf.S
i387 float `atanf`/`_atanf` implementation using x87 float argument setup. Read: 23 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_atanf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceil.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceil.S
i387 double `ceil` implementation that temporarily changes the x87 control word to round toward positive infinity, rounds, and restores state. Read: 45 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceil.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceilf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceilf.S
i387 float `ceilf` implementation that rounds toward positive infinity via temporary x87 control-word changes. Read: 43 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ceilf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysign.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysign.S
i387 double `copysign` implementation using bit-level sign replacement around x87 return handling. Read: 38 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysign.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysignf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysignf.S
i387 float `copysignf` implementation using bit-level sign replacement. Read: 37 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_copysignf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finite.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finite.S
i387 double `finite`/`_finite` implementation that checks exponent bits against the infinity/NaN encoding. Read: 29 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finite.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finitef.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finitef.S
i387 float `finitef`/`_finitef` implementation that checks float exponent bits. Read: 28 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_finitef.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floor.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floor.S
i387 double `floor` implementation that temporarily rounds toward negative infinity and restores the x87 control word. Read: 43 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floor.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floorf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floorf.S
i387 float `floorf` implementation using temporary x87 control-word changes for round-toward-negative-infinity. Read: 43 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_floorf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ilogbl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ilogbl.S
i387 long-double `ilogbl` implementation using x87 long-double argument handling and exponent extraction. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_ilogbl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1p.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1p.S
i387 double `log1p`/`_log1p` implementation choosing between `fyl2x` and `fyl2xp1` paths for accuracy. Read: 78 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1p.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1pf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1pf.S
i387 float `log1pf`/`_log1pf` implementation choosing between `fyl2x` and `fyl2xp1` paths. Read: 78 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_log1pf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logb.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logb.S
i387 double `logb` implementation using x87 exponent-oriented operations. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logb.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbf.S
i387 float `logbf` implementation using x87 exponent-oriented operations. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbl.S
i387 long-double `logbl` implementation using x87 long-double argument handling. Read: 16 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_logbl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rint.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rint.S
i387 double `rint` implementation using x87 `frndint` under the current rounding mode. Read: 17 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rint.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintf.S
i387 float `rintf` implementation using x87 `frndint`. Read: 17 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintl.S
i387 long-double `rintl` implementation using x87 `frndint`. Read: 39 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_rintl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbn.S
i387 double `scalbn`, `scalbln`, and `ldexp` implementation using x87 `fscale` and alias entries. Read: 46 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnf.S
i387 float `scalbnf`, `scalblnf`, and `ldexpf` implementation using x87 `fscale`. Read: 47 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnl.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnl.S
i387 long-double `scalbnl`, `scalblnl`, and `ldexpl` implementation using x87 `fscale`. Read: 41 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_scalbnl.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_significand.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_significand.S
i387 double `significand` implementation using x87 argument handling. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_significand.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_significandf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_significandf.S
i387 float `significandf` implementation using x87 argument handling. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/i387/s_significandf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/ia64/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/ia64/fenv.c
IA-64 fenv compatibility source. It supplies `feupdateenv`, restoring an environment while preserving/raising previously pending exception flags. Read: 91 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/ia64/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/Makefile -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/Makefile
m68060 build fragment for generated assembly wrappers and FPSP support. It coordinates generated source lists, `fplsp.hex`, and wrapper build artifacts. Read: 23 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_acos.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_acos.S
m68060 generated wrapper for double `__ieee754_acos`, calling the FPSP/FPLSP routine at its assigned offset. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_acos.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_acosf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_acosf.S
m68060 generated wrapper for float `__ieee754_acosf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_acosf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_asin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_asin.S
m68060 generated wrapper for double `__ieee754_asin`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_asin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_asinf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_asinf.S
m68060 generated wrapper for float `__ieee754_asinf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_asinf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_atanh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_atanh.S
m68060 generated wrapper for double `__ieee754_atanh`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_atanh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_atanhf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_atanhf.S
m68060 generated wrapper for float `__ieee754_atanhf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_atanhf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_cosh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_cosh.S
m68060 generated wrapper for double `__ieee754_cosh`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_cosh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_coshf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_coshf.S
m68060 generated wrapper for float `__ieee754_coshf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_coshf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_exp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_exp.S
m68060 generated wrapper for double `__ieee754_exp`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_exp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_expf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_expf.S
m68060 generated wrapper for float `__ieee754_expf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_expf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log.S
m68060 generated wrapper for double `__ieee754_log`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log10.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log10.S
m68060 generated wrapper for double `__ieee754_log10`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log10.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log10f.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log10f.S
m68060 generated wrapper for float `__ieee754_log10f`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_log10f.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_logf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_logf.S
m68060 generated wrapper for float `__ieee754_logf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_logf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinh.S
m68060 generated wrapper for double `__ieee754_sinh`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinhf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinhf.S
m68060 generated wrapper for float `__ieee754_sinhf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sinhf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrt.S
m68060 generated wrapper for double `__ieee754_sqrt`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrtf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrtf.S
m68060 generated wrapper for float `__ieee754_sqrtf`. Read: 22 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/e_sqrtf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/fplsp_wrap.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/fplsp_wrap.S
m68060 wrapper glue that includes `fplsp.hex`, exposing Motorola FPLSP/FPSP binary support entry points to generated wrappers. Read: 15 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/fplsp_wrap.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/k_tan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/k_tan.S
m68060 placeholder for kernel tangent support; it exports no runtime routine in this file. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/k_tan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/k_tanf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/k_tanf.S
m68060 placeholder for float kernel tangent support; it exports no runtime routine in this file. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/k_tanf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeas.sh -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeas.sh
Shell generator for m68060 assembly wrappers. It maps libm symbols to fixed FPLSP/FPSP offsets, emits `ENTRY`/alias assembly, and produces generated source/list artifacts. Read: 237 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeas.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeoffs.awk -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeoffs.awk
Awk helper that emits `ENTRY_NOPROFILE(__fplsp060_xxxx)` labels for FPLSP offset entry points. Read: 9 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/makeoffs.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_atan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_atan.S
m68060 generated wrapper for double `atan`/`_atan`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_atan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_atanf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_atanf.S
m68060 generated wrapper for float `atanf`/`_atanf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_atanf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_cos.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_cos.S
m68060 generated wrapper for double `cos`/`_cos`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_cos.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_cosf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_cosf.S
m68060 generated wrapper for float `cosf`/`_cosf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_cosf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1.S
m68060 generated wrapper for double `expm1`/`_expm1`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1f.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1f.S
m68060 generated wrapper for float `expm1f`/`_expm1f`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_expm1f.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_log1p.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_log1p.S
m68060 generated wrapper for double `log1p`/`_log1p`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_log1p.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_log1pf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_log1pf.S
m68060 generated wrapper for float `log1pf`/`_log1pf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_log1pf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_logb.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_logb.S
m68060 generated wrapper for double `logb`/`_logb`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_logb.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_logbf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_logbf.S
m68060 generated wrapper for float `logbf`/`_logbf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_logbf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_sin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_sin.S
m68060 generated wrapper for double `sin`/`_sin`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_sin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_sinf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_sinf.S
m68060 generated wrapper for float `sinf`/`_sinf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_sinf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tan.S
m68060 generated wrapper for double `tan`/`_tan`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanf.S
m68060 generated wrapper for float `tanf`/`_tanf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanh.S
m68060 generated wrapper for double `tanh`/`_tanh`. Read: 26 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanhf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanhf.S
m68060 generated wrapper for float `tanhf`/`_tanhf`. Read: 24 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68060/s_tanhf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/fenv.c
m68k fenv compatibility source. It establishes namespace/header wiring but no substantial out-of-line fenv implementation in this file. Read: 75 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_ceil.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_ceil.S
m68k `ceil` implementation that saves FPCR, sets round-toward-positive-infinity, performs integer rounding, restores FPCR, and returns the result. Read: 57 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_ceil.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_copysign.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_copysign.S
m68k `copysign`/`copysignl` implementation that copies the sign of one operand onto the magnitude of another. Read: 72 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_copysign.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_finite.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_finite.S
m68k `finite`/`_finite` implementation that tests exponent encodings for finite double values. Read: 55 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_finite.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_floor.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_floor.S
m68k `floor` implementation that saves FPCR, sets round-toward-negative-infinity, rounds, restores FPCR, and returns. Read: 58 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_floor.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_rint.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_rint.S
m68k `rint` implementation using the prevailing FP rounding mode. Read: 52 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/m68k/s_rint.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_acos.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_acos.S
mc68881 double `__ieee754_acos` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_acos.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_asin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_asin.S
mc68881 double `__ieee754_asin` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_asin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_atanh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_atanh.S
mc68881 double `__ieee754_atanh` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_atanh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_cosh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_cosh.S
mc68881 double `__ieee754_cosh` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_cosh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_exp.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_exp.S
mc68881 double `__ieee754_exp` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_exp.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_fmod.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_fmod.S
mc68881 double `__ieee754_fmod` implementation using Motorola FP remainder support. Read: 20 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_fmod.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_log.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_log.S
mc68881 double `__ieee754_log` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_log.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_log10.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_log10.S
mc68881 double `__ieee754_log10` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_log10.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_remainder.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_remainder.S
mc68881 double `__ieee754_remainder` implementation using Motorola FP remainder support. Read: 20 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_remainder.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_scalb.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_scalb.S
mc68881 double `__ieee754_scalb` implementation using `fscale`/scale-by-exponent behavior. Read: 20 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_scalb.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sinh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sinh.S
mc68881 double `__ieee754_sinh` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sinh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sqrt.S
mc68881 double `__ieee754_sqrt` implementation using `fsqrtd`. Read: 56 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/e_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_atan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_atan.S
mc68881 double `atan`/`_atan` implementation using Motorola FP instructions. Read: 53 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_atan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_cos.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_cos.S
mc68881 double `cos`/`_cos` implementation using Motorola FP instructions. Read: 53 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_cos.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_expm1.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_expm1.S
mc68881 double `expm1` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_expm1.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_log1p.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_log1p.S
mc68881 double `log1p`/`_log1p` implementation using Motorola FP instructions. Read: 53 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_log1p.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_logb.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_logb.S
mc68881 `logb` implementation that handles NaN/infinity cases and extracts the unbiased exponent. Read: 69 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_logb.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_scalbn.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_scalbn.S
mc68881 `scalbn`, `scalbln`, and `ldexp` implementation using `fscale`-style scaling and aliases. Read: 58 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_scalbn.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_sin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_sin.S
mc68881 double `sin`/`_sin` implementation using Motorola FP instructions. Read: 53 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_sin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tan.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tan.S
mc68881 double `tan`/`_tan` implementation using Motorola FP instructions. Read: 53 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tan.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tanh.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tanh.S
mc68881 double `tanh` implementation using Motorola FP instructions. Read: 50 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mc68881/s_tanh.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mips/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/mips/fenv.c
MIPS fenv compatibility source. It sets namespace/header wiring; actual behavior is supplied by inline definitions, softfloat support, or architecture-selected code. Read: 78 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/mips/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/fenv.c
PowerPC fenv compatibility source with namespace/header wiring and no substantial out-of-line implementation in this file. Read: 74 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fma.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fma.S
PowerPC double `fma` implementation using `fmadd`, with `fmal` weak aliasing to `fma`. Read: 14 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fma.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fmaf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fmaf.S
PowerPC float `fmaf` implementation using `fmadds`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/powerpc/s_fmaf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrt.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrt.S
RISC-V double `__ieee754_sqrt` implementation using `fsqrt.d`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrt.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrtf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrtf.S
RISC-V float `__ieee754_sqrtf` implementation using `fsqrt.s`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/e_sqrtf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/fenv.c
RISC-V fenv implementation. It reads/writes `fflags`, `frm`, and `fcsr` CSRs for exception flags, rounding mode, environment save/restore, hold/update, and trap controls. Read: 294 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrint.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrint.S
RISC-V `lrint`/`llrint` conversion routine using `fcvt` from double to integer width selected by ABI. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrint.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrintf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrintf.S
RISC-V `lrintf`/`llrintf` conversion routine using `fcvt` from float to integer width selected by ABI. Read: 18 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/lrintf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysign.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysign.S
RISC-V double `copysign` implementation using `fsgnj.d`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysign.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysignf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysignf.S
RISC-V float `copysignf` implementation using `fsgnj.s`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_copysignf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabs.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabs.S
RISC-V double `fabs` implementation using `fabs.d`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabs.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabsf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabsf.S
RISC-V float `fabsf` implementation using `fabs.s`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fabsf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fma.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fma.S
RISC-V double `fma` implementation using `fmadd.d`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fma.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaf.S
RISC-V float fused multiply-add implementation using `fmadd.s`; entry symbol is `fmaddf` in this source. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmax.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmax.S
RISC-V double `fmax` implementation using `fmax.d`, with `fmaxl` aliasing where appropriate. Read: 15 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmax.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaxf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaxf.S
RISC-V float `fmaxf` implementation using `fmax.s`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmaxf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmin.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmin.S
RISC-V double `fmin` implementation using `fmin.d`, with `fminl` aliasing where appropriate. Read: 15 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fmin.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fminf.S -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fminf.S
RISC-V float `fminf` implementation using `fmin.s`. Read: 10 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/riscv/s_fminf.S -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/sh3/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/sh3/fenv.c
SH3 fenv compatibility source. It provides namespace/header wiring; actual fenv behavior is supplied elsewhere depending on build configuration. Read: 70 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/sh3/fenv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/sparc/fenv.c -->
# File Research: sources/os/bsd/netbsd-src/lib/libm/arch/sparc/fenv.c
SPARC fenv implementation. It reads/writes FSR fields for exception flags, rounding mode, environment save/restore, hold/update, and enabled exception masks. Read: 348 lines.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/lib/libm/arch/sparc/fenv.c -->