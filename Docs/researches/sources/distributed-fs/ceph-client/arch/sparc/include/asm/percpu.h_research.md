# sources/distributed-fs/ceph-client/arch/sparc/include/asm/percpu.h

Purpose: selects `percpu_64.h` or `percpu_32.h` from `CONFIG_SPARC64` so generic kernel code can include one SPARC per-CPU entry point.

Important APIs/types/functions: macros/constants `___ASM_SPARC_PERCPU_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PERCPU_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/percpu_64.h`, `asm/percpu_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
