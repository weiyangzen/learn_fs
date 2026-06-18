# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vclock_gettime.c

Purpose: builds the 32-bit SPARC vDSO time implementation, including compat 32-bit vDSO on a 64-bit kernel.

Important APIs/macros: defines `BUILD_VDSO32`; under `CONFIG_SPARC64` it undefines 64-bit config macros, defines `BUILD_VDSO32_64` and `CONFIG_32BIT`, and disables queued lock config macros before including `../vclock_gettime.c`.

Control flow: no independent functions; inclusion reuses the common vclock source under a faked 32-bit compile environment.

State and persistence: no owned state; generated symbols come from the included common file.

Dependencies and integration points: used by the vDSO Makefile for `vdso32.so.dbg`, depends on generic vDSO time code and compat ABI expectations.

Risks: macro environment must not leak incompatible 64-bit assumptions into 32-bit userspace code. Symbol set must include both legacy and time64 clock entry points.

Test signals: compat tasks calling `clock_gettime`, `clock_gettime64`, and `gettimeofday`; build with `CONFIG_COMPAT`; inspect 32-bit ELF class and symbols.
