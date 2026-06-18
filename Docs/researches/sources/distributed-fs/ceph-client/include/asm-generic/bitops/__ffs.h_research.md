# sources/distributed-fs/ceph-client/include/asm-generic/bitops/__ffs.h

Purpose: Implements generic `__ffs()` to find the zero-based index of the least significant set bit in an unsigned long.

Important APIs, types, and functions: Defines `generic___ffs(unsigned long word)` and maps `__ffs(word)` to it unless the architecture provides `__HAVE_ARCH___FFS`.

Control flow: Tests progressively smaller low-bit chunks, shifting right and accumulating 32/16/8/4/2/1 offsets. Input zero is explicitly undefined and must be checked by callers.

State and persistence: No state.

Dependencies and integration points: Depends on `BITS_PER_LONG` and asm types. Used by bitmap scanning, `ffz`, and generic bitops.

Risks and test signals: Risks are zero input misuse and 32/64-bit branch errors. Test powers of two, mixed-bit words, 32-bit and 64-bit builds, and callers’ zero guards.
