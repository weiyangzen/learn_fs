## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia-ntt.c

Purpose: bundled NTT Camellia block cipher core. It implements key schedule generation and single-block encryption/decryption for 128-, 192-, and 256-bit keys.

Important APIs/functions/macros: public APIs are `Camellia_Ekeygen()`, `Camellia_EncryptBlock()`, and `Camellia_DecryptBlock()`. Internal key schedule functions are `camellia_setup128()`, `camellia_setup192()`, and `camellia_setup256()`. Internal block functions are `camellia_encrypt128()`, `camellia_decrypt128()`, `camellia_encrypt256()`, and `camellia_decrypt256()`, with the 192-bit path using the 256-bit schedule after complement expansion. Macros implement endian load/store (`GETU32`, `PUTU32`), rotations, subkey indexing, F function, FL/FLINV layer, and round operations. Four 256-entry SP tables and six Sigma constants drive the Camellia transforms.

Control flow: `Camellia_Ekeygen()` dispatches by key length and fills a 272-byte/68-word key table. For 128-bit keys, the schedule derives KL and KA subkeys, performs rotations, absorbs whitening keys into subkeys, and applies inverse P-function transforms. For 192-bit keys, it builds a synthetic 256-bit key by appending bitwise complements of the final 64 bits, then calls the 256-bit schedule. For 256-bit keys, it derives KL, KR, KA, and KB dependent subkeys. Encrypt/decrypt APIs load four big-endian words from a 16-byte block, dispatch by key size, then write four big-endian words to output.

State and persistence: no global mutable state. Static SP tables are read-only. Caller-owned `KEY_TABLE_TYPE` persists generated subkeys. Stack temporaries hold sensitive key material during setup and are not explicitly zeroized before return.

Dependencies: `config.h`, `<string.h>`, `<stdlib.h>`, `<krb5-types.h>`, `camellia-ntt.h`, and `roken.h`. The MSVC path uses `_lrotl`/`_lrotr` and unaligned casts; the non-MSVC path performs byte loads/stores.

Integration points: wrapped by `camellia.c`, which exposes OpenSSL-like `CAMELLIA_*` APIs, and by `evp-hcrypto.c` through Camellia CBC EVP ciphers.

Risks: invalid key lengths fall through without error in `Camellia_Ekeygen()`, `Camellia_EncryptBlock()`, and `Camellia_DecryptBlock()`, potentially leaving stale key tables or copying unchanged temporary data. Key setup stack temporaries are not wiped. Table-driven S-box operations are data-dependent memory lookups and may not be constant-time on all platforms. The MSVC `GETU32` path casts input bytes to `u32 *`, which can have alignment/aliasing concerns outside MSVC assumptions.

Test signals: official Camellia known-answer vectors for 128/192/256-bit keys, round-trip block tests, invalid key length behavior tests, big-endian load/store checks on little/big endian platforms, and integration through `CAMELLIA_*` and EVP CBC wrappers.
