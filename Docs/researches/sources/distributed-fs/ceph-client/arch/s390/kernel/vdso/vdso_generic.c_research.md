## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso_generic.c

Purpose: Thin s390 wrappers around generic vDSO time implementations.

Important APIs: `__s390_vdso_gettimeofday()`, `__s390_vdso_clock_gettime()`, and `__s390_vdso_clock_getres()`.

Control flow: Includes `lib/vdso/gettimeofday.c` and forwards each s390-named wrapper to the corresponding `__cvdso_*` implementation.

State and persistence: Uses generic vDSO data page state through included code; this file owns no state.

Dependencies and integration: Depends on common vDSO time code, vDSO datapage, and assembly wrappers that export `__kernel_*` symbols calling these `__s390_vdso_*` functions.

Risks and test signals: Risks are ABI/type mismatch and architecture data setup errors outside this file. Test signals include vDSO clock/gettimeofday correctness versus syscalls and clocksource mode transitions.
