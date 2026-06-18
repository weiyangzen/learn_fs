# sources/distributed-fs/ceph-client/arch/arc/lib/memcpy-700.S

Purpose: ARCompact/ARC700 optimized `memcpy()`.

Important APIs/functions: exports `memcpy` through `ENTRY_CFI(memcpy)`.

Control flow: tests source/destination alignment and length. Aligned copies load/store words in a zero-overhead loop, with special handling for a 4-byte chunk and final partial word using endian-specific masking. Unaligned or small cases fall back to bytewise copy using load/store byte loops.

State and persistence: no persistent state; returns original destination in `r0` while copying through `r5`.

Dependencies and integration: selected by `arch/arc/lib/Makefile` for `CONFIG_ISA_ARCOMPACT`. Relies on ARC700 instruction scheduling, delay slots, auto-increment addressing, and endian-aware final masking.

Risks: `memcpy()` does not guarantee overlap safety; callers must use `memmove()` for overlapping ranges. Partial final word logic can accidentally touch bytes outside the range if masks are wrong. Alignment detection drives correctness and performance.

Test signals: copy tests across small lengths, aligned/unaligned src/dst combinations, final byte counts 1-7, endian builds, and overlap-negative tests confirming callers do not misuse `memcpy()`.
