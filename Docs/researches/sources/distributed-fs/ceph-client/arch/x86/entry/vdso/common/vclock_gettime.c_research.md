## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/common/vclock_gettime.c

Purpose: common vDSO wrappers for fast user-mode `gettimeofday`, `time`, `clock_gettime`, and `clock_getres` implementations.

Important APIs/functions: `__vdso_gettimeofday`, weak `gettimeofday`, `__vdso_time`, weak `time`, `__vdso_clock_gettime`, weak `clock_gettime`, `__vdso_clock_getres`, weak `clock_getres`, and for i386 `__vdso_clock_gettime64`/`__vdso_clock_getres_time64`. It includes `lib/vdso/gettimeofday.c` to reuse generic vDSO time logic.

Control flow: exported wrappers immediately delegate to `__cvdso_*` helpers. Compile-time conditions select 64-bit/x32 `__kernel_timespec` APIs or i386 `old_timespec32` plus time64 variants.

State/persistence: no writable state here; it reads shared vDSO/VVAR data through the generic vDSO implementation.

Integration points: vDSO linker version scripts, VVAR data pages, timekeeping core, compat 32-bit ABI, libc symbol lookup through weak aliases, and build flags from vDSO Makefiles.

Risks: ABI signatures and symbol names are user-visible and must match version scripts. Time32/time64 selection is sensitive to build defines such as `BUILD_VDSO32_64`. Test signals include vDSO time selftests, libc fallback tests, 32-bit and x32 execution, symbol-version inspection, and time namespace/timekeeping tests.
