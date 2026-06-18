# sources/distributed-fs/ceph-client/include/crypto/cast5.h

Purpose: CAST5 cipher constants, context, and primitive operation declarations.

Important APIs/types/functions: `CAST5_BLOCK_SIZE`, key size bounds, `struct cast5_ctx`, `cast5_setkey`, `__cast5_encrypt`, and `__cast5_decrypt`.

Control flow: setkey fills masking/rotation subkeys and selects reduced/full rounds; block helpers encrypt/decrypt one block with prepared context.

State and persistence: context stores 16 masking subkeys, 16 rotation subkeys, and round selector.

Dependencies and integration points: depends on CAST common S-box declarations and crypto core types.

Risks: 64-bit block size limits safe data volume. Round selector must match RFC 2144 key-size behavior.

Test signals: CAST5 known-answer tests, reduced-round key tests, and crypto mode tests.
