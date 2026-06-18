# sources/distributed-fs/ceph-client/arch/sparc/include/asm/pil.h

Purpose: Constant/ABI header for `pil.h` supplying numeric definitions consumed by low-level SPARC code.

Important APIs/types/functions: macros/constants `_SPARC64_PIL_H`, `PIL_SMP_CALL_FUNC`, `PIL_SMP_RECEIVE_SIGNAL`, `PIL_SMP_CAPTURE`, `PIL_DEVICE_IRQ`, `PIL_SMP_CALL_FUNC_SNGL`, `PIL_DEFERRED_PCR_WORK`, `PIL_KGDB_CAPTURE`, `PIL_NORMAL_MAX`, `PIL_NMI`.

Control flow: The file is driven by preprocessor gates such as `_SPARC64_PIL_H`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into SMP paths rather than through standalone functions.

State and persistence behavior: State is external hardware or ABI state represented by constants; the header itself has no mutable storage.

Dependencies and integration points: Includes/dependencies: none beyond compiler-visible SPARC/kernel types. Integration points include SMP; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are macro collision or stale declaration risk. Test signals: Compile-time users plus boot/runtime paths that decode these constants are the main tests.
