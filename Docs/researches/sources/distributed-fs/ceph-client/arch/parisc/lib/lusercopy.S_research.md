# sources/distributed-fs/ceph-client/arch/parisc/lib/lusercopy.S

Purpose: provides low-level PA-RISC user access routines: `lclear_user()` and `pa_memcpy()`. The code is assembly because it must use space-register-qualified loads/stores, recover from access faults through exception table entries, and optimize common aligned copies.

Important APIs/types/functions: `lclear_user(to, n)` zeroes user memory in space register 3 and returns bytes not cleared. `pa_memcpy(dst, src, len)` copies between spaces already installed in `sr1` and `sr2`; C wrappers in `memcpy.c` set those registers for user or kernel copies.

Control flow: `lclear_user` is a byte loop with an exception fixup that returns the remaining count. `pa_memcpy` chooses a byte path for short copies, aligned 64-bit or 32-bit unrolled loops when source and destination alignment matches, and a destination-aligned unaligned-source path that combines adjacent words with `shrpw`. Faulting loads/stores branch to fixups that compute the uncopied byte count. Some doubleword/word load faults store the already loaded partial data before returning.

State and dependencies: no memory state outside the copied buffers and no persistence. It depends on PA-RISC calling conventions, temporary register aliases, `ASM_EXCEPTIONTABLE_ENTRY`, and caller-provided source/destination space registers.

Risks: tiny register or fixup mistakes can corrupt user memory or report the wrong residual byte count. Overlap semantics are memcpy-like, not memmove-like. Exception-table coverage must exactly match every faulting memory instruction. 64-bit and 32-bit paths diverge under `CONFIG_64BIT`.

Test signals: usercopy fault-injection tests, partial-copy residual checks across page boundaries, alignment matrix tests for source/destination offsets and lengths, KASAN/usercopy hardening tests, and PA-RISC boot or syscall workloads that stress `copy_to_user` and `copy_from_user`.
