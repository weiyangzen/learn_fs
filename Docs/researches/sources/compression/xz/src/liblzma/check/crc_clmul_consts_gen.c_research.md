# sources/compression/xz/src/liblzma/check/crc_clmul_consts_gen.c

Purpose: developer utility that derives carry-less multiplication constants used by the x86 PCLMUL CRC32/CRC64 implementation.

Important APIs/types/functions: constants `p32` and `p64`, helper `calc_cldiv(uint64_t p)`, helper `calc_clrem(uint64_t p, unsigned bits)`, and `main()`.

Control flow: `calc_cldiv()` computes Barrett reduction reciprocal-style values using carry-less division over GF(2). `calc_clrem()` computes polynomial remainders for powers used in folding. `main()` prints constant groups for CRC32 and CRC64 that correspond to 512-bit folding, 128-bit folding, and Barrett reduction parameters used in `crc_x86_clmul.h`.

State and persistence: no runtime library state. Its persistent output is manually copied into CLMUL source constants.

Dependencies/integration: includes `inttypes.h` and `stdio.h`. The generated values are embedded in `crc_x86_clmul.h`; they must align with the reversed CRC32 and CRC64 polynomials used elsewhere.

Risks: this file is not part of normal runtime, so mistakes can enter through manual constant updates. Polynomial arithmetic is subtle; off-by-one degree assumptions or 64-bit truncation mistakes break only the optimized path. Printed constants must be checked against known vectors after updating.

Test signals: after regenerating constants, run CRC32/CRC64 known vectors with CLMUL forced and compare against generic implementations. Code review should also map each printed constant to the corresponding `fold512`, `fold128`, and `mu_p` initializer.
