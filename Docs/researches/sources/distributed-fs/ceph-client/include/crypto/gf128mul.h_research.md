# sources/distributed-fs/ceph-client/include/crypto/gf128mul.h

Purpose: GF(2^128) multiplication primitives and table helpers for multiple endian/bit-order conventions.

Important APIs/types/functions: `gf128mul_lle`, `gf128mul_mask_from_bit`, `gf128mul_x_lle`, `gf128mul_x_bbe`, `gf128mul_x_ble`, `gf128mul_x8_ble`, `struct gf128mul_64k`, `gf128mul_init_64k_bbe`, `gf128mul_free_64k`, and `gf128mul_64k_bbe`.

Control flow: inline multiply-by-x helpers load endian-specific words, compute reduction masks branchlessly, shift the field element, and conditionally apply reduction constants. Table helpers precompute 64 KiB lookup state for faster bbe multiplication.

State and persistence: table objects allocate precomputed multiplication tables and must be freed. Inline helpers are stateless.

Dependencies and integration points: depends on byteorder, `b128ops`, and slab allocation. Used by GCM/GHASH, XTS, LRW, and other block modes over GF(2^128).

Risks: endian convention confusion (`lle`, `bbe`, `ble`) is the dominant correctness risk. Table allocation failure must be handled. Constant-time mask logic should not be replaced by branches in sensitive paths.

Test signals: GF multiplication vectors for all conventions, XTS/GHASH/LRW mode tests, big/little-endian runtime coverage, table-vs-generic comparison, and allocation failure tests.
