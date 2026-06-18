# sources/distributed-fs/lizardfs/src/common/galois_field.h

Purpose: declares the finite-field matrix/table/encoding API used for Reed-Solomon erasure coding.

Important APIs/types/functions: `gf_gen_rs_matrix`, `gf_gen_cauchy1_matrix`, `gf_invert_matrix`, `ec_init_tables`, and `ec_encode_data`.

Control flow: callers generate an encoding matrix, invert matrices for recovery, initialize 32-byte-per-coefficient tables, and encode/decode source buffers into destination buffers.

State and persistence: no state in header; implementations use caller-provided buffers.

Dependencies and integration: depends on `<cstdint>` and `platform.h`. It abstracts ISA-L-derived finite-field routines for `ReedSolomon` and EC read/write paths.

Risks: raw pointer API has no dimension/bounds validation. Matrix inversion mutates its input matrix. Buffer aliasing and alignment requirements are implementation-sensitive.

Test signals: EC planner tests indirectly validate recovery; no direct GF unit tests in this subset.
