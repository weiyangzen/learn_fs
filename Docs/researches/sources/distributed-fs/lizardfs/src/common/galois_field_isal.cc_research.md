# sources/distributed-fs/lizardfs/src/common/galois_field_isal.cc

Purpose: ISA-L-derived finite-field support for matrix generation, inversion, coefficient table initialization, and GF multiplication/inversion.

Important APIs/types/functions: `gf_mul`, `gf_inv`, `gf_gen_rs_matrix`, `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `gf_vect_mul_init`, and `ec_init_tables`.

Control flow: `gf_mul` and `gf_inv` use compile-time log/exp tables. Matrix generators write identity data rows plus parity rows. `gf_invert_matrix` performs Gauss-Jordan elimination with row swapping over GF(2^8), mutating input and writing inverse. `gf_vect_mul_init` expands a coefficient into low/high nibble tables, with optimized 64-bit layout when available. `ec_init_tables` repeats table expansion for each row/coefficient.

State and persistence: no internal mutable global state; all outputs go to caller-provided buffers.

Dependencies and integration: depends on `galois_coeff.h`, `cstring`, and ISA-L algorithm conventions. Used by Reed-Solomon code backing EC reads/writes.

Risks: raw pointer matrix dimensions are unchecked. `gf_inv(0)` returns zero, which is convenient but mathematically undefined; callers must avoid zero pivots except where handled. Matrix inversion mutates input, which can surprise callers.

Test signals: no direct GF tests; EC read plan tests indirectly exercise recovery correctness.
