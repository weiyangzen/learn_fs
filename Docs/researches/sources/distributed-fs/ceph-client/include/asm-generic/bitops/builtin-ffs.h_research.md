# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-ffs.h

Purpose: Defines `ffs()` through the compiler builtin with libc-compatible one-based indexing.

Important APIs, types, and functions: Macro `ffs(x)` expands to `__builtin_ffs(x)`.

Control flow: Delegated to the compiler. Unlike `__ffs`, `ffs(0)` returns 0.

State and persistence: No state.

Dependencies and integration points: Depends on compiler `__builtin_ffs`. Used by integer and bitmap helpers expecting libc-style semantics.

Risks and test signals: Risks are confusing one-based `ffs()` with zero-based `__ffs()`. Test `ffs(0)`, `ffs(1)`, high bits, and callers converting between index conventions.
