# sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu_64.h

Purpose: sparc64 per-CPU addressing header binding the per-CPU base to global register `%g5` and, under SMP, to `trap_block[cpu].__per_cpu_base`.

Important APIs/types/functions: functions/helpers `asm`; macros/constants `__ARCH_SPARC64_PERCPU__`, `__per_cpu_offset`, `per_cpu_offset`, `__my_cpu_offset`.

Control flow: The file is driven by preprocessor gates such as `__ARCH_SPARC64_PERCPU__`, `BUILD_VDSO`, `CONFIG_SMP`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP, VDSO paths rather than through standalone functions.

State and persistence behavior: Persistent state is per-CPU trap-block storage plus the register-resident `__local_per_cpu_offset`; VDSO builds intentionally avoid the register declaration.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`, `asm/trap_block.h`, `asm-generic/percpu.h`. Integration points include SMP, VDSO; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are configuration-specific build gaps. Test signals: Boot CPU bring-up, secondary CPU per-CPU variable access, VDSO builds, and context switch preservation of `%g5` are the key signals.
