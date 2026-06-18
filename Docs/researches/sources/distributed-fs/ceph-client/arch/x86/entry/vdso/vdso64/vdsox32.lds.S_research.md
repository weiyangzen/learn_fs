## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/vdsox32.lds.S

Purpose: x32 vDSO linker/version script.

Important declarations: defines `BUILD_VDSOX32`, includes common layout, and exports the x32 vDSO set: `__vdso_clock_gettime`, `__vdso_gettimeofday`, `__vdso_getcpu`, `__vdso_time`, and `__vdso_clock_getres`.

Control flow: link-time only; visibility is narrower than the native 64-bit script.

State/persistence: defines the x32 ABI vDSO symbol table in an ELF32-x86-64 image containing 64-bit code.

Integration points: vdso64 Makefile x32 objcopy/link path, x32 process setup, and common vDSO layout.

Risks: x32 symbol ABI is distinct from both i386 and x86_64; exporting the wrong surface can confuse libc. Test signals include x32 build/readelf checks and x32 userspace time/getcpu tests.
