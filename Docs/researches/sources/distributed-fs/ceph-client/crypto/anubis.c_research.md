# sources/distributed-fs/ceph-client/crypto/anubis.c

Purpose: implements the generic Linux Crypto API provider for the Anubis 128-bit block cipher. It registers `anubis-generic` as a `CRYPTO_ALG_TYPE_CIPHER` algorithm with 16-byte blocks and 16, 20, 24, 28, 32, 36, or 40 byte keys.

Important APIs/types/functions: `struct anubis_ctx` stores key length, round count, and encryption/decryption round key arrays. The large `T0` through `T5` tables and `rc` constants drive the tweaked Anubis key schedule and round function. `anubis_setkey()` validates key length, derives encryption round keys, and builds the inverse schedule. `anubis_crypt()` performs common block transformation, while `anubis_encrypt()` and `anubis_decrypt()` select `ctx->E` or `ctx->D`. `anubis_alg`, `anubis_mod_init()`, and `anubis_mod_fini()` provide module registration.

Control flow: module load calls `crypto_register_alg()`. Consumers allocate a cipher transform, call the setkey hook, then call single-block encrypt/decrypt hooks. Key expansion maps big-endian key words into `kappa`, iterates `R = 8 + key_words` rounds, and computes decryption keys by reversing and transforming encryption keys. Crypting reads four big-endian words, applies the initial key, executes `R - 1` table rounds, executes a masked final round, and writes big-endian output.

State and persistence: all runtime state is per-transform memory in `struct anubis_ctx`; the lookup tables are read-only module data. There is no disk persistence. Sensitive key schedule material is stored until the transform is freed by the crypto core.

Dependencies and integration points: depends on `crypto/algapi.h`, module init/exit, unaligned big-endian helpers, and the classic cipher `cra_u.cipher` interface. It integrates with any kernel code that requests `"anubis"` or `"anubis-generic"`.

Risks: table-based cipher code is not constant-time with respect to lookup indices, so side-channel suitability depends on deployment context. Key-size validation is strict but unusual because Anubis accepts seven key lengths. Round-table or inverse-schedule corruption would break interoperability. The old single-block cipher interface is lower-level than modern skcipher/lskcipher users normally want.

Test signals: crypto selftests should include known-answer vectors for all accepted key lengths, encrypt/decrypt round trips, invalid key length rejection, module load/unload, and algorithm lookup aliases.
