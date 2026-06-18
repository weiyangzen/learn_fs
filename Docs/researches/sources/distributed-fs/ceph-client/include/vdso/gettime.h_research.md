<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/gettime.h -->
# sources/distributed-fs/ceph-client/include/vdso/gettime.h

Purpose: declares vDSO time-related exported functions for clock_gettime, clock_getres, time, gettimeofday, and time64 variants.

Important APIs and types: function prototypes switch between `old_timespec32` and `__kernel_timespec` depending on 64-bit/compat build. Exports include `__vdso_clock_getres`, `__vdso_clock_gettime`, `__vdso_time`, `__vdso_gettimeofday`, `__vdso_clock_gettime64`, and `__vdso_clock_getres_time64`.

Control flow: libc resolves these vDSO symbols and calls them before falling back to syscalls; generic/arch vDSO implementations read VVAR data and fill caller-provided time structures.

State and persistence: no state in the header. Functions consume shared VVAR state from `vdso/datapage.h`.

Dependencies and integration points: depends on Linux time types and forward declarations. It integrates with libc symbol resolution, compat vDSO builds, and kernel-generated vDSO images.

Risks and test signals: risks include wrong prototype for compat builds, time32 overflow, and symbol ABI mismatch. Test 32-bit and 64-bit vDSO symbol calls, libc fallback behavior, Y2038/time64 paths, and invalid clock IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/vdso/gettime.h -->
