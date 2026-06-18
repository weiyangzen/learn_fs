# sources/distributed-fs/ceph-client/arch/mips/lib/strncpy_user.S

Purpose: implements assembly backend for copying a NUL-terminated string from user space.

Important APIs/functions: exports `__strncpy_from_user_asm`; uses exception macro `EX` and EVA `lbue` when configured.

Control flow: loops byte-by-byte from user source to kernel destination until NUL or count limit, increments copied count, checks for pointer wrap into kernel space, returns copied length/count, or returns `-EFAULT` via exception-table fixup.

State and persistence: writes destination buffer; no global state.

Dependencies and integration: used by MIPS `strncpy_from_user`; depends on exception tables, EVA user-load instruction, and R10K barrier macro.

Risks: user pointer wrap handling is a special-case guard; faults after partial copy return `-EFAULT` rather than partial length. Byte loop favors correctness over speed.

Test signals: usercopy string tests, fault injection on invalid user pointers, limit-boundary behavior, and EVA build/run coverage.
