# sources/distributed-fs/ceph-client/arch/sparc/vdso/Makefile

Purpose: builds SPARC vDSO shared objects, converts them into kernel-embedded images, and builds vDSO VMA setup code.

Important APIs/targets: builds `vma.o`, `vdso-image-64.o` for `CONFIG_SPARC64`, and `vdso-image-32.o` for compat. Links `vdso64.so.dbg` and `vdso32.so.dbg`, strips `.so` files, and runs host tool `vdso2c`.

Control flow: kbuild compiles vDSO objects with PIC, no stack protector, no branch profiling, frame pointers kept, and SPARC register flags filtered out. It links with `vdso.lds` or `vdso32.lds`, validates through generic vDSO checks, strips, then embeds via generated C.

State and persistence: build-time only; generated images are compiled into the kernel.

Dependencies and integration points: depends on generic `lib/vdso/Makefile.include`, host `vdso2c`, SPARC linker emulations, compat toolchain flags, and vDSO source/linker scripts.

Risks: vDSO must be relocation-free and use correct page size/ELF ABI. Toolchain flags are delicate because vDSO runs in userspace but is built inside the kernel tree.

Test signals: sparc64 and compat builds, `readelf` checks for no relocations and expected symbols, vDSO selftests for `clock_gettime`, `gettimeofday`, and mapping behavior.
