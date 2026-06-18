## sources/distributed-fs/ceph-client/arch/s390/kernel/vdso/Makefile

Purpose: Builds the s390 vDSO shared object, wrapper object, stripped DSO, debug DSO, and generated vDSO offset header.

Important targets and variables: `obj-vdso`, `obj-cvdso`, `VDSO_CFLAGS_REMOVE`, `KBUILD_AFLAGS_VDSO`, `KBUILD_CFLAGS_VDSO`, `ldflags-y`, `vdso.so.dbg`, `vdso.so`, `vdso_wrapper.o`, `vdso.lds`, and `include/generated/vdso-offsets.h`.

Control flow: The makefile removes kernel-only instrumentation flags from vDSO objects, adds PIC/no-stack-protector/vDSO-specific flags, links `vdso.so.dbg` with `vdso.lds` first, runs the generic vDSO checker, strips to `vdso.so`, compiles assembly and C vDSO objects with special commands, forces wrapper rebuild after `vdso.so`, and generates offset defines by piping `nm` through `gen_vdso_offsets.sh`.

State and persistence: Persistent build outputs are the vDSO objects, debug/stripped DSOs, wrapper object, linker script output, and generated offset header.

Dependencies and integration: Uses `lib/vdso/Makefile.include`, optional generated getrandom include, s390 vDSO source files, linker script, `NM`, `OBJCOPY`, and the kernel object that incbins `vdso.so`.

Risks and test signals: Risks are accidentally retaining tracing/profiling flags, DSO ABI/check failures, stale offsets, and dependency misses around incbin. Test signals include clean/incremental kernel builds, `cmd_vdso_check`, generated `vdso-offsets.h`, and runtime vDSO symbol resolution.
