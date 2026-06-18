## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/vclock_gettime.c

Purpose: includes the common vDSO time implementation for the 32-bit image.

Important dependency: `#include "common/vclock_gettime.c"`. Under vdso32 build flags this selects i386 time32 plus time64 wrapper variants.

Control flow: all exported behavior comes from the included common source and delegates to generic `__cvdso_*` helpers.

State/persistence: reads VVAR time data through the common implementation; no local state.

Integration points: vdso32 Makefile fake 32-bit config, vDSO version script, libc time calls, and kernel VVAR mappings.

Risks: inclusion relies on build defines to select correct ABI types. Test signals include 32-bit `clock_gettime`, `clock_gettime64`, `gettimeofday`, and symbol-version checks.
