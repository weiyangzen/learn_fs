# sources/distributed-fs/ceph-client/arch/sparc/vdso/vdso32/vdso32.lds.S

Purpose: defines the SPARC32 vDSO linker/version script.

Important APIs/sections: sets `BUILD_VDSO32`, includes the common layout, and exports `clock_gettime`, `__vdso_clock_gettime`, `clock_gettime64`, `__vdso_clock_gettime64`, `gettimeofday`, and `__vdso_gettimeofday` in version `LINUX_2.6`.

Control flow: used by the Makefile when linking `vdso32.so.dbg`.

State and persistence: build-time symbol ABI only.

Dependencies and integration points: depends on symbols emitted by the 32-bit vclock source and dynamic linker/libc vDSO probing.

Risks: omitting `clock_gettime64` would break modern 32-bit time64 users. Extra globals would expand ABI unintentionally.

Test signals: `readelf --dyn-syms --version-info` on the 32-bit vDSO and compat time syscall/vDSO selftests.
