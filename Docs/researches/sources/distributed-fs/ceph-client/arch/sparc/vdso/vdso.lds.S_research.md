# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso.lds.S

Purpose: defines the SPARC64 vDSO linker/version script.

Important APIs/sections: sets `BUILD_VDSO64`, includes the common layout script, and exports version `LINUX_2.6` symbols `clock_gettime`, `__vdso_clock_gettime`, `gettimeofday`, and `__vdso_gettimeofday`; all other symbols are local.

Control flow: used by the Makefile as the linker script for `vdso64.so.dbg`.

State and persistence: build-time symbol versioning only.

Dependencies and integration points: depends on `vdso-layout.lds.S` and function names emitted by `vclock_gettime.c`. Userland dynamic linkers resolve these symbols through the mapped vDSO.

Risks: missing or extra global symbols are ABI changes. Symbol names must match libc probing conventions.

Test signals: `readelf --dyn-syms --version-info` on the 64-bit vDSO should show only the intended `LINUX_2.6` globals.
