# sources/distributed-fs/ceph-client/arch/sh/lib/__clear_user.S

Purpose: implements the MMU-enabled SH `__clear_user` primitive that zeroes user memory and reports bytes not cleared on fault.

Important symbols: `ENTRY(__clear_user)`, loop labels for byte/long clearing, and `.Lbad_clear_user` exception-table recovery.

Control flow: validates length, aligns to longword boundaries, clears leading/trailing bytes and aligned longwords, then returns zero. Exception table entries redirect faulting stores to cleanup logic that computes the remaining byte count for uaccess callers.

State and persistence: mutates user memory only; no persistent kernel state.

Dependencies and integration: depends on `linux/linkage.h`, `asm/page.h`, SH exception-table fixups, and generic uaccess paths.

Risks: off-by-one recovery or alignment errors can under-report failed bytes or overwrite unintended user memory. The code is tightly coupled to exception-table addresses.

Test signals: uaccess fault-injection tests, copy/clear-user selftests, and page-boundary clearing cases.
