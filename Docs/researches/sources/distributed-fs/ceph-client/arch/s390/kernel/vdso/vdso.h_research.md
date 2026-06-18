## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/vdso.h

Purpose: Declares internal s390 vDSO C entry points and the getrandom ABI wrapper.

Important declarations: `__s390_vdso_getcpu()`, `__s390_vdso_gettimeofday()`, `__s390_vdso_clock_gettime()`, `__s390_vdso_clock_getres()`, and `__kernel_getrandom()`.

Control flow: Header-only contract shared by vDSO C files and assembly wrappers.

State and persistence: No state.

Dependencies and integration: Includes `vdso/datapage.h` for vDSO time data types and is included by getcpu, generic time wrappers, and getrandom implementation.

Risks and test signals: Risks are prototype mismatches with assembly-exported names or user ABI expectations. Test signals are vDSO build warnings/errors and symbol ABI checks.
