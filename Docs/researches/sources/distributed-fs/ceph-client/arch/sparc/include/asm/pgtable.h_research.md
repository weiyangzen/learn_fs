# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pgtable.h

Purpose: routes generic MM code to `pgtable_64.h` or `pgtable_32.h`, hiding the very different Spitfire/SRMMU page table encodings.

Important APIs/types/functions: macros/constants `___ASM_SPARC_PGTABLE_H`.

Control flow: The file is driven by preprocessor gates such as `___ASM_SPARC_PGTABLE_H`, `defined(__sparc__) && defined(__arch64__)`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into low-level SPARC architecture code paths rather than through standalone functions.

State and persistence behavior: It owns no runtime storage; its state effect is compile-time routing through `CONFIG_SPARC64` so consumers see one stable include path.

Dependencies and integration points: Includes/dependencies: `asm/pgtable_64.h`, `asm/pgtable_32.h`. Integration points include low-level SPARC architecture code; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Build both SPARC32 and SPARC64 configurations and include it from generic kernel subsystems to catch missing symbols or wrong branch selection.
