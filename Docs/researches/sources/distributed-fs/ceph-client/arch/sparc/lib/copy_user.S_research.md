# sources/distributed-fs/ceph-client/arch/sparc/lib/copy_user.S

Purpose: SPARC32 user-copy implementation with exception handling.

Important APIs/functions: Exports `__copy_user` and marks `__copy_user_begin`/`__copy_user_end`.

Control flow: Contains optimized dword/word/byte copy paths, alignment tables, and fixup labels for big chunks, last chunks, half chunks, and short chunks. Exception table macros redirect faults to code that computes remaining bytes and returns.

State and persistence: No persistent state; mutates destination and relies on exception-table metadata.

Dependencies/integration: Includes `asm/ptrace.h`, `asm/asmmacro.h`, `asm/page.h`, and `asm/thread_info.h`; built for `CONFIG_SPARC32`.

Risks/test signals: Fixup tables must cover every faulting access. Test user copy fault injection, alignment table paths, small/large copies, and begin/end metadata consumers.
