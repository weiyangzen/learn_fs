## sources/distributed-fs/ceph-client/arch/x86/entry/vdso/vdso32/Makefile

Purpose: builds the 32-bit x86 vDSO image `linux-gate.so.1`.

Important build variables: `vdsos-y := 32`, `vobjs-y := note.o vclock_gettime.o vgetcpu.o system_call.o sigreturn.o`, `flags-y := -DBUILD_VDSO32 -m32 -mregparm=0`, optional include of `fake_32bit_build.h` on x86_64, `flags-remove-y := -m64`, adjusted `CHECKFLAGS`, included `../common/Makefile.include`, and `VDSO_LDFLAGS_32`.

Control flow: Kbuild compiles 32-bit objects, applies fake 32-bit config when cross-building from x86_64, and links `vdso32.so.dbg` from the vDSO objects.

State/persistence: produces the 32-bit vDSO binary consumed by kernel mapping code and exported to 32-bit tasks.

Integration points: common vDSO source files, 32-bit signal/syscall assembly, linker script, sparse checking, and compat execution.

Risks: wrong flags can build ABI-incompatible code or leak x86_64 config into a 32-bit image. Test signals include 32-bit vDSO build under x86_64, sparse checks, readelf class/soname validation, and 32-bit userspace smoke tests.
