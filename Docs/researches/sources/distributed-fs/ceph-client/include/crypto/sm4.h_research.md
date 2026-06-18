# sources/distributed-fs/ceph-client/include/crypto/sm4.h

Purpose: declares SM4 block cipher constants, context, key expansion tables, and block primitive.

Important APIs, types, and flow: constants define 16-byte key/block sizes and 32 round-key words. `struct sm4_ctx` stores encryption and decryption round keys. Extern tables expose FK, CK, and S-box constants. `sm4_expandkey()` prepares round keys from a raw key; `sm4_crypt_block()` encrypts/decrypts one block with a selected round-key array.

State and persistence: round keys live in caller-owned/transform context and are sensitive. No persistence exists.

Dependencies and integration: used by SM4 crypto drivers and mode templates.

Risks and test signals: risks include key schedule endian handling, encrypt/decrypt round-key ordering, and table access side-channel concerns. Signals include SM4 known-answer vectors, mode self-tests, optimized/generic parity, and key zeroization review.
