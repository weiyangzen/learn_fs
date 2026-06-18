# sources/distributed-fs/ceph-client/arch/x86/include/asm/vdso/gettimeofday.h

Purpose: Implements x86 architecture hooks for generic vDSO time functions: fast hardware counter reads, syscall fallbacks, cycle validation, and nanosecond conversion rules.

Important APIs/types/functions: `VDSO_HAS_TIME` and `VDSO_HAS_CLOCK_GETRES` enable generic vDSO exports. `clock_gettime_fallback()`, `gettimeofday_fallback()`, `clock_getres_fallback()`, and 32-bit variants use `VDSO_SYSCALL*` macros. `vread_pvclock()` reads KVM/Xen pvclock when `CONFIG_PARAVIRT_CLOCK` is enabled. `vread_hvclock()` reads Hyper-V reference TSC page when `CONFIG_HYPERV_TIMER` is enabled. `__arch_get_hw_counter()` dispatches TSC, pvclock, or Hyper-V clock reads. `arch_vdso_clocksource_ok()` currently accepts all provided clocksources. `arch_vdso_cycles_ok()` rejects negative/sentinel cycle values. `vdso_calc_ns()` performs x86-specific delta validation and ns conversion.

Control flow: Generic vDSO time code reads the vDSO datapage clock mode and calls `__arch_get_hw_counter()`. TSC uses `rdtsc_ordered()`. Paravirtual and Hyper-V modes are guarded by compiler barriers before touching mapped clock pages, because those pages can fault if the mode is disabled. Returned cycles are validated, then `vdso_calc_ns()` compares against `cycle_last`, clamps negative motion to base time, handles overflow with `mul_u64_u32_add_u64_shr()`, and otherwise applies `delta * mult + base`.

State and persistence: Reads shared, kernel-updated vDSO time data and optional hypervisor pages `pvclock_page` and `hvclock_page`. It stores no state locally. The code treats `U64_MAX` and sign-bit-set values as invalid counter reads.

Dependencies and integration points: Depends on x86 MSR/TSC helpers, pvclock, Hyper-V timer definitions, `asm/vgtod.h`, generic vDSO datapage structures, and `asm/vdso/sys_call.h`. It is central to user-space `clock_gettime`, `gettimeofday`, and `time` performance.

Risks: Barrier placement is critical; speculative or compiler-hoisted loads from disabled clock pages can segfault. TSC skew across sockets requires the custom delta clamp. Hypervisor clock invalidation must be treated as fallback-worthy. 32-bit syscall suffix selection must remain aligned with syscall numbering.

Test signals: vDSO time selftests, monotonicity tests under CPU migration, KVM/Xen/Hyper-V guest tests, fallback syscall tracing, and build coverage for 32-bit and 64-bit configs with and without paravirtual clocks.
