# sources/distributed-fs/ceph-client/include/asm-generic/bitops/builtin-__fls.h

Purpose: Provides compiler-builtin `__fls()` using count-leading-zero support.

Important APIs, types, and functions: Defines `__fls(unsigned long word)` as word width minus one minus `__builtin_clzl(word)`.

Control flow: Delegates to compiler builtin; zero input is undefined.

State and persistence: No state.

Dependencies and integration points: Depends on `__builtin_clzl` and correct `sizeof(word)` width. Used by generic bitops when builtin implementations are selected.

Risks and test signals: Risks are zero input, wrong width assumptions, and compiler lowering differences. Test boundary values, top-bit values, 32/64-bit targets, and generated assembly.
