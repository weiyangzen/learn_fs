<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/Makefile -->
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/Makefile

Purpose: Build orchestration for the PowerPC kernel core, selecting objects, instrumentation exclusions, flags, generated linker scripts, and vDSO wrapper dependencies.

Important APIs/types/functions: Object lists `obj-y`, config-gated `obj-*`/`obj64-*`, CFLAGS/KASAN/KCSAN/KCOV/GCOV/UBSAN controls, prom init check rule, vDSO wrapper prerequisites, and clean/subdir declarations.

Control flow: Kbuild evaluates architecture configs, removes tracing/sanitizer instrumentation from early or translation-off code, builds core objects and optional platform/feature modules, runs `prom_init_check`, forces vDSO wrapper dependencies, and includes vdso as a subdir.

State and persistence: No runtime state; it controls build artifacts and object inclusion. Built objects persist in the kernel image/modules.

Dependencies and integration points: Depends on Kbuild variables, PowerPC config symbols, compiler option helpers, `prom_init_check.sh`, vdso outputs, and generated `vmlinux.lds`.

Risks: Instrumentation in early boot or real-mode code can make kernels unbootable. Missing config-gated objects break feature paths such as KVM, RTAS, XIVE, EEH, or CPU setup.

Test signals: PowerPC defconfig/allmodconfig builds across PPC32/PPC64, sanitizer-enabled builds, vdso dependency rebuilds, and prom_init check execution.

Source read size: 220 lines, 7388 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/kernel/Makefile -->
