# sources/distributed-fs/ceph-client/arch/mips/lib/strnlen_user.S

Purpose: implements assembly backend for bounded user-string length calculation.

Important APIs/functions: exports `__strnlen_user_asm`; uses exception macro `EX` and EVA `lbe` when configured.

Control flow: computes stop pointer from start plus max length, scans one byte at a time until limit or NUL, returns length including the terminating NUL, and returns zero on fault.

State and persistence: reads user memory only.

Dependencies and integration: used by MIPS `strnlen_user`/`strlen_user`; depends on exception tables, EVA, and CPU DADDI workarounds.

Risks: comments note deliberate limited access into low KSEG0 for performance. Address wrap and 64-bit boundary behavior are delicate.

Test signals: user-string length tests for NUL, no-NUL limit, invalid pointer, and EVA/non-EVA builds.
