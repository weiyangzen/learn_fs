# File Research: sources/cow-pools/bcachefs-tools/include/linux/jhash.h

This header implements Jenkins lookup3 hash helpers. It defines `jhash_size()`, `jhash_mask()`, the reversible mix/final macros, `JHASH_INITVAL`, and inline functions `jhash()`, `jhash2()`, `jhash_1word()`, `jhash_2words()`, and `jhash_3words()`.

`jhash()` consumes arbitrary byte keys using unaligned 32-bit loads for full 12-byte blocks and a fallthrough switch for the tail. `jhash2()` handles arrays of `u32`. Results are 32-bit and depend on endianness for byte keys.
