## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vclock_gettime.c

Purpose: includes common vDSO time wrappers for 64-bit and x32 images.

Important dependency: `#include "common/vclock_gettime.c"`, with `BUILD_VDSO64` selecting 64-bit/x32 signatures.

Control flow: exported functions call generic `__cvdso_*` helpers through the common source.

State/persistence: no local state; reads VVAR timekeeping data.

Integration points: 64-bit version script, libc time APIs, vDSO VVAR mapping, timekeeping core, and x32 conversion.

Risks: type/signature mismatches are ABI regressions. Test signals include `clock_gettime`, `gettimeofday`, `time`, `clock_getres` vDSO selftests on x86_64 and x32, plus symbol-version checks.
