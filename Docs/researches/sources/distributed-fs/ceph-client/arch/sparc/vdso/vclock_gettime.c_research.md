# sources/distributed-fs/ceph-client/arch/sparc/vdso/vclock_gettime.c

Purpose: provides SPARC vDSO user-visible fast time functions by wrapping the generic vDSO gettimeofday implementation.

Important APIs/functions: defines `__vdso_gettimeofday()` and weak alias `gettimeofday()`. For 64-bit builds it defines `__vdso_clock_gettime()` and `clock_gettime()` using `__kernel_timespec`; for 32-bit builds it also defines 32-bit `clock_gettime()` and time64 `__vdso_clock_gettime64()`.

Control flow: each exported function delegates directly to `__cvdso_gettimeofday()`, `__cvdso_clock_gettime()`, or `__cvdso_clock_gettime32()`. The file includes `lib/vdso/gettimeofday.c` into the vDSO object.

State and persistence: reads kernel-provided vvar/vdso data pages through generic vDSO code; owns no persistent state.

Dependencies and integration points: depends on `vdso/gettime.h`, SPARC `asm/vdso/gettimeofday.h`, vvar mapping, and symbol version scripts.

Risks: vDSO code must have no unresolved relocations and cannot rely on kernel-only instrumentation. 32-bit/time64 ABI symbol selection must match userspace expectations.

Test signals: vDSO `clock_gettime`, `clock_gettime64`, `gettimeofday`, and `time` tests on 64-bit and compat tasks; compare against syscall fallback under clocksource changes.
