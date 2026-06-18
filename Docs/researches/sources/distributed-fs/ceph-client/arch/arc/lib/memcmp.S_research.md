# sources/distributed-fs/ceph-client/arch/arc/lib/memcmp.S

Purpose: optimized ARC assembly implementation of `memcmp()`.

Important APIs/functions: exports `memcmp` via `ENTRY_CFI(memcmp)`. Uses endian-specific register roles and comparison extraction logic.

Control flow: checks combined alignment and length to choose wordwise or bytewise path. Wordwise path loads paired words, uses zero-overhead loops, compares even/odd words, then isolates the first differing byte. Bytewise path handles unaligned or short buffers. ARCv2 has special loop placement because a branch cannot be the last instruction in a zero-overhead loop.

State and persistence: no persistent state; clobbers scratch registers per ABI and returns comparison result in `r0`.

Dependencies and integration: used by generic kernel code through lib linkage. Depends on ARC instructions such as `lpne`, `norm`, `bmsk`, endian macros, and CFI linkage macros.

Risks: first-difference selection is subtle and endian-specific. Off-by-one length handling or loop scheduling mistakes would corrupt sorting/comparison semantics. Zero-length and unaligned inputs are important edge cases.

Test signals: memcmp tests for equal, first/last-byte difference, every length around 0-16, unaligned source pairs, endian variants, and ARCv2 zero-overhead-loop builds.
