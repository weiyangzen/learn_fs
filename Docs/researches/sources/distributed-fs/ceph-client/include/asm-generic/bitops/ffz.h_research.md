# sources/distributed-fs/ceph-client/include/asm-generic/bitops/ffz.h

Purpose: Defines `ffz()` to find the zero-based index of the first zero bit in a word.

Important APIs, types, and functions: Macro `ffz(x)` expands to `__ffs(~(x))`.

Control flow: Inverts the word and delegates to `__ffs`; input with no zero bits is undefined and must be guarded by callers.

State and persistence: No state.

Dependencies and integration points: Depends on `__ffs`. Used by bitmap allocation and low-level bit scanning.

Risks and test signals: Risks include all-ones input misuse and word-size assumptions. Test zero word, all-ones guarded cases, mixed bitmaps, and allocation scans near word boundaries.
