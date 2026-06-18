# sources/distributed-fs/ceph-client/include/crypto/sm3.h

Purpose: declares direct SM3 hash constants, context, and incremental/one-shot APIs.

Important APIs, types, and flow: constants define digest/block sizes and initial vector words. `sm3_block_state` and `sm3_ctx` hold incremental state, byte count, and partial block. `sm3_init()`, `sm3_update()`, `sm3_final()`, and `sm3()` implement hashing.

State and persistence: caller-owned context only; no persistence.

Dependencies and integration: used by SM2/SM4-related protocols and generic hash users requiring SM3.

Risks and test signals: risks include endian and padding differences from SHA-style code. Signals include SM3 standard vectors, split-update tests, empty-message tests, and optimized/generic parity.
