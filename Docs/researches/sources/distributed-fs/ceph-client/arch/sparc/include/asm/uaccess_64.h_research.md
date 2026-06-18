# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_64.h

Purpose: sparc64 user-memory accessor implementation using secondary ASI loads/stores, exception-table fixups, kernel nofault helpers, range checks, raw copy declarations, and effective-address decoding.

Important APIs/types/functions: types `__large_struct`, `pt_regs`; functions/helpers `__chk_range_not_ok`, `__retl_efault`, `__volatile__`, `raw_copy_from_user`, `raw_copy_to_user`, `raw_copy_in_user`, `__clear_user`, `strnlen_user`, `compute_effective_address`; macros/constants `_ASM_UACCESS_H`, `__range_not_ok`, `put_user`, `get_user`, `__put_user`, `__get_user`, `__m`, `__put_kernel_nofault`, `__put_kernel_asm`, `__put_user_nocheck`, `__put_user_asm`, `__get_kernel_nofault`, `__get_kernel_asm`, `__get_user_nocheck`, `__get_user_asm`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`, `clear_user`.

Control flow: The file is driven by preprocessor gates such as `_ASM_UACCESS_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, user-copy, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is caller/user memory plus exception-table control flow; user ASIs isolate user VM from kernel VM, and fixup paths return `-EFAULT`.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`, `linux/string.h`, `linux/mm_types.h`, `asm/asi.h`, `asm/spitfire.h`, `asm/pgtable.h`, `asm/processor.h`, `asm-generic/access_ok.h`. Integration points include memory-management, user-copy, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, inline assembly or ASI ordering mistakes. Test signals: Bad pointer fault tests, compat user copy, nofault kernel probes, raw_copy_in_user, clear_user, and unaligned effective-address handling are signals.
