# sources/distributed-fs/ceph-client/arch/sparc/lib/memset.S

Purpose: optimized SPARC assembly implementation of `memset`, `__bzero`, and clear-user-style zeroing helpers. It supports normal kernel memset return semantics and exception-table fixups for user-memory clearing.

Important APIs/functions: `memset(dst, c, len)` returns the original destination. `__bzero(dst, len)` zeros a region and returns zero on success or remaining bytes on clear-user exceptions. Labels `__bzero_begin` and `__bzero_end` delimit the region for exception/fixup users. Macros `EX`, `STORE`, `STORE_LAST`, `ZERO_BIG_BLOCK`, and `ZERO_LAST_BLOCKS` generate fault-aware byte/word/doubleword stores and exception table records.

Control flow: `memset` saves original `%o0`, replicates the low byte of `%o1` into a 32-bit pattern, then shares the bzero body with `%g4` set so it returns the original pointer. The common body aligns to 4 and then 8 bytes, stores repeated 128-byte chunks via unrolled 64-byte blocks, handles remaining 8-byte groups through a computed jump into `ZERO_LAST_BLOCKS`, then finishes 4/2/1-byte tails. The `.fixup` path computes how many bytes remain after a fault and returns through label `30`.

State and persistence: writes caller-specified memory only. It writes exception table entries and fixup code at assembly time, not runtime. No global runtime state.

Dependencies/integration: includes `linux/export.h` and `asm/ptrace.h`; emits `__ex_table` entries used by the kernel exception-table search. `EXPORT_SYMBOL(__bzero)` and `EXPORT_SYMBOL(memset)` make this the SPARC implementation used broadly by core kernel and modules.

Risks: the generated fixup math is tightly coupled to the store macros; changing macro order or offsets can make clear-user remaining-byte results wrong. Alignment arithmetic must preserve `memset`'s original-pointer return while `__bzero` returns zero. Large unrolled stores increase the blast radius of a single exception-table bug.

Test signals: boot-time/string selftests for memset patterns, zero lengths, unaligned destinations, and every tail size 0-127. Usercopy/clear_user tests should verify exception fixup return counts across faults in byte, word, doubleword, and block stores. Disassembly review should confirm `.fixup` and `__ex_table` entries align with store sites.
