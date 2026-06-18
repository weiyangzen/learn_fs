# sources/distributed-fs/ceph-client/include/asm-generic/bitops/__fls.h

Purpose: Implements generic `__fls()` to find the zero-based index of the most significant set bit in an unsigned long.

Important APIs, types, and functions: Defines `generic___fls(unsigned long word)` and maps `__fls(word)` unless `__HAVE_ARCH___FLS` is set.

Control flow: Starts at `BITS_PER_LONG - 1`, tests high chunks, left-shifts the word when the high chunk is empty, and subtracts offsets until the top set bit is located. Input zero is undefined.

State and persistence: No state.

Dependencies and integration points: Depends on `BITS_PER_LONG` and asm types. Used by bitmap sizing, integer log calculations, and generic bitops.

Risks and test signals: Risks are zero input misuse, top-bit edge cases, and 32/64-bit shift mistakes. Test zero-guarded callers, highest bit set, lowest bit set, random values, and both word sizes.
