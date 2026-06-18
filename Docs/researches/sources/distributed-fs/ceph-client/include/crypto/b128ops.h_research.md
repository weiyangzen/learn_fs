# sources/distributed-fs/ceph-client/include/crypto/b128ops.h

Purpose: common 128-bit block element representations and XOR helpers.

Important APIs/types/functions: `be128`, `le128`, `be128_xor`, and `le128_xor`.

Control flow: inline helpers XOR two 128-bit values word-by-word into a result.

State and persistence: none beyond caller-supplied 128-bit values.

Dependencies and integration points: used by GF(2^128), XTS/GHASH/LRW-style operations and any code needing typed endian 128-bit blocks.

Risks: endian-specific structs are not interchangeable; using `be128` where `le128` is expected changes polynomial interpretation.

Test signals: finite-field mode KATs and endian conversion tests.
