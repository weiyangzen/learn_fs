# sources/distributed-fs/ceph-client/arch/xtensa/lib/strnlen_user.S

Purpose: Computes bounded userspace string length including the trailing NUL, returning zero on fault.

Important APIs, types, and functions: `__strnlen_user`, endian masks, alignment prologue, word scanning loop, byte-position zero handlers, fault fixup returning zero, and `EXPORT_SYMBOL`.

Control flow: Adjusts pointer bookkeeping to use word loads, handles odd and halfword-aligned starts, scans full words for zero bytes, checks remaining bytes, and returns distance from original pointer including NUL when found or bounded length when exhausted.

State and persistence: Read-only userspace access; no internal state.

Dependencies and integration: User access exception table, string/usercopy APIs, Xtensa endian and alignment behavior.

Risks: The aligned loop performs a word load for remaining checks, so exception fixup must protect boundary cases; return convention differs from plain `strlen` by including NUL and using zero for fault.

Test signals: `strnlen_user` tests for all alignments, NUL positions, no NUL within bound, faulting page at first byte and at boundary, and big-endian builds.
