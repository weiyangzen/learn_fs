# sources/distributed-fs/ceph-client/arch/sparc/include/asm/uaccess_32.h

Purpose: SPARC32 user-memory accessor implementation with `get_user`/`put_user`, inline ASI load/store fixups, raw copy declarations, clear/string helpers, and range checking through generic `access_ok`.

Important APIs/types/functions: types `__large_struct`; functions/helpers `__volatile__`, `__copy_user`, `raw_copy_to_user`, `raw_copy_from_user`, `__clear_user`, `clear_user`, `strnlen_user`; macros/constants `_ASM_UACCESS_H`, `put_user`, `get_user`, `__put_user`, `__get_user`, `__m`, `__put_user_check`, `__put_user_nocheck`, `__put_user_asm`, `__get_user_check`, `__get_user_nocheck`, `__get_user_asm`, `INLINE_COPY_FROM_USER`, `INLINE_COPY_TO_USER`.

Control flow: The file is driven by preprocessor gates such as `_ASM_UACCESS_H`; inline/assembler paths that run at trap, MMU, cache, lock, or user-copy boundaries; static inline helpers selected by generic kernel call sites. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into user-copy, scheduler/task paths rather than through standalone functions.

State and persistence behavior: State is not persistent except caller memory; exception-table fixups convert data faults to `-EFAULT` and zero failed reads.

Dependencies and integration points: Includes/dependencies: `linux/compiler.h`, `linux/string.h`, `asm/processor.h`, `asm-generic/access_ok.h`. Integration points include user-copy, scheduler/task; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are inline assembly or ASI ordering mistakes. Test signals: Fault injection on bad user pointers, copy_to/from_user, clear_user, string length/from-user helpers, and size-specific accessors are tests.
