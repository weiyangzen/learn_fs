# sources/distributed-fs/ceph-client/lib/crypto/x86/polyval-pclmul-avx.S

## Purpose
AVX/PCLMULQDQ implementation of POLYVAL field multiplication and block evaluation. It evaluates eight 16-byte blocks per stride using precomputed powers `h^8..h^1` and reduces modulo `x^128 + x^127 + x^126 + x^121 + 1`.

## APIs, Control Flow, And Integration
Exports `polyval_mul_pclmul_avx(struct polyval_elem *a, const struct polyval_elem *b)` and `polyval_blocks_pclmul_avx(struct polyval_elem *acc, const struct polyval_key *key, const u8 *data, size_t nblocks)`. Macros `schoolbook1*` compute 128x128 polynomial products into `LO/MI/HI`, `schoolbook2` forms `[PH:PL]`, and `montgomery_reduction` folds with `.Lgstar`. The blocks function handles full eight-block strides, reduces the previous product while starting the next stride, then handles 1..7 residual blocks with an adjusted key-power pointer.

## State, Dependencies, Risks, And Tests
Only `acc` is persisted and updated in place; key powers and input are read-only. It depends on Linux linkage/frame macros and caller-side AVX/PCLMUL/FPU dispatch. Risks are key-power layout mismatch, wrong POLYVAL endian/modulus assumptions, and callers passing partial blocks. Tests should compare against generic POLYVAL for block counts 1..9, random multiplication, and AES-GCM-SIV known-answer vectors.
