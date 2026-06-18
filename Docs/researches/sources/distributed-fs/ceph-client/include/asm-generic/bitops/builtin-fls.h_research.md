# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-fls.h

Purpose: Defines `fls()` through compiler count-leading-zero support with one-based result semantics.

Important APIs, types, and functions: Inline `fls(unsigned int x)` returns `sizeof(x) * 8 - __builtin_clz(x)` or 0 for `x == 0`.

Control flow: Explicitly handles zero, otherwise delegates to `__builtin_clz`.

State and persistence: No state.

Dependencies and integration points: Depends on compiler `__builtin_clz`. Used by power-of-two, sizing, and bitmap helpers.

Risks and test signals: Risks are one-based versus zero-based confusion and incorrect assumptions for non-`unsigned int` callers. Test zero, one, `0x80000000`, and random values against generic `fls`.
