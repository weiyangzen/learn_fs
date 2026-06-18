# sources/distributed-fs/ceph-client/crypto/sm4.c

`sm4.c` implements the shared generic SM4 block cipher library: constants, S-box, key expansion, and single-block crypt operation. Registration is handled by `sm4_generic.c`.

Exported symbols are `crypto_sm4_fk`, `crypto_sm4_ck`, `crypto_sm4_sbox`, `sm4_expandkey()`, and `sm4_crypt_block()`. Internal helpers perform nonlinear S-box substitution, key and encryption linear transforms, key substitution, encryption substitution, and one SM4 round.

`sm4_expandkey()` validates a 16-byte key, loads it big-endian, xors FK constants, derives 32 round keys using CK constants, stores encryption keys forward, and stores decryption keys reversed. `sm4_crypt_block()` loads a 16-byte block big-endian, runs 32 rounds four at a time with the provided round-key array, and stores the reversed output words. State is caller-owned `struct sm4_ctx`; constants are static exported read-only data. Dependencies include `<crypto/sm4.h>` and unaligned big-endian helpers. Risks are endian correctness, reverse decryption key layout, setkey failure handling, and table-lookup side channels. Test signals include SM4 vectors, encrypt/decrypt round trips, and `tcrypt` SM4 modes.
