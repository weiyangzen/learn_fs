# sources/distributed-fs/ceph-client/crypto/ripemd.h

Purpose: defines shared RIPEMD constants used by RIPEMD-family implementations, currently consumed by `rmd160.c`.

Important APIs and data: provides `RMD160_DIGEST_SIZE`, `RMD160_BLOCK_SIZE`, initial state words `RMD_H0` through `RMD_H4`, and round constants `RMD_K1` through `RMD_K9`.

Control flow: none. This is a guarded header of macro constants.

State and persistence: none; values are compile-time constants.

Dependencies and integration points: included by `rmd160.c` to name the algorithm sizes and compression-function constants. Any future RIPEMD variants can share the same header for common IVs and constants where appropriate.

Risks: changing constants silently breaks digest compatibility. Macro names are global within includers, so additional RIPEMD headers should avoid collisions.

Test signals: RIPEMD-160 known-answer vectors indirectly validate these constants. Compile coverage ensures the include guard and macro definitions remain available.
