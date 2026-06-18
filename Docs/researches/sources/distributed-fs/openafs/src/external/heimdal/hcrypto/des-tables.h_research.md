## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/des-tables.h

Purpose: generated lookup tables for DES key schedule setup and parity adjustment.

Important APIs/types/data: static arrays `pc1_c_3`, `pc1_c_4`, `pc1_d_3`, `pc1_d_4`, `pc2_c_1` through `pc2_c_4`, `pc2_d_1` through `pc2_d_4`, and `odd_parity[256]`. The PC1/PC2 arrays encode DES key permutation/compression bit patterns used by `DES_set_key_unchecked()`. `odd_parity` maps each byte to an odd-parity-adjusted byte.

Control flow: no functions; `des.c` includes this header directly and indexes the arrays while constructing subkeys and checking/setting key parity.

State and persistence: all arrays are `static` at include site. They are mutable by type except `odd_parity` is also static non-const, but intended as read-only generated data. No persistence outside the process.

Dependencies: none directly, but it assumes inclusion in a C source context where `static int` and `static unsigned char` definitions are valid.

Integration points: tightly coupled to `des.c`; not a standalone public header. The top comment says it is generated from `gen-des.pl` and should not be edited manually.

Risks: because arrays are not `const`, accidental writes in the including translation unit could corrupt DES behavior. Generated-table correctness is critical and opaque to casual review. Including this header in more than one source creates separate static copies.

Test signals: DES key schedule known-answer vectors, parity mapping tests for all 256 byte values, and regeneration comparison against the generator if available.
