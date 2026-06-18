## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso64/Makefile

Purpose: builds 64-bit and optional x32 vDSO images.

Important build variables: `vdsos-y := 64`, optional `x32`, `vobjs-y := note.o vclock_gettime.o vgetcpu.o vgetrandom.o vgetrandom-chacha.o`, optional `vsgx.o`, `flags-y := -DBUILD_VDSO64 -m64 -mcmodel=small`, common Makefile include, x32 objcopy rule, `VDSO_LDFLAGS_64`, and `VDSO_LDFLAGS_x32`.

Control flow: 64-bit objects are linked directly into `vdso64.so.dbg`; x32 builds reuse 64-bit code objects converted to `elf32-x86-64` before linking `vdsox32.so.dbg`.

State/persistence: creates vDSO image blobs referenced by `vdso64_image` and `vdsox32_image`.

Integration points: vDSO random, SGX, time/getcpu wrappers, linker scripts, Kbuild objcopy, and process exec mapping.

Risks: x32 conversion and symbol selection are ABI-sensitive. Test signals include x86_64 and x32 vDSO builds, readelf class/soname checks, getrandom/time/getcpu selftests, and SGX-enabled build coverage.
