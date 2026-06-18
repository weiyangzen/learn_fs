# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/test_cipher.c

Purpose: standalone cipher known-answer test program for hcrypto provider descriptors, with optional Apple CommonCrypto provider comparisons.

Important APIs/types/functions: `struct tests` holds cipher name, key, key size, IV, data size, input, expected output, and optional expected IV. Static vectors cover AES-256-CBC, AES-128-CFB8, RC2-40-CBC, 3DES-CBC, Camellia-128-CBC, and RC4. `test_cipher` initializes encrypt/decrypt EVP contexts, sets key length, encrypts, compares hex-encoded failures, decrypts, and compares plaintext. `main` parses `--help`/`--version` and runs provider tests.

Control flow: each vector is tested by creating separate encrypt/decrypt contexts, initializing with descriptor then key/IV, invoking single-shot `EVP_Cipher`, checking ciphertext, decrypting in place, and cleaning contexts. Apple-only tests compile under `__APPLE__`.

State and persistence: no persistent state beyond static test vectors. Failures terminate with `errx`; success returns accumulated zero count.

Dependencies and integration points: depends on `evp.h`, `evp-hcrypto.h`, optional `evp-cc.h`, `getarg`, `hex`, `err`, and `roken`. It exercises provider descriptors rather than low-level primitives directly.

Risks and test signals: coverage is useful but narrow: most tests are one-block or stream single-shot, IV output checks are TODO, and padding/update APIs are not covered. Test improvements should add segmented `EVP_CipherUpdate/Final`, IV mutation expectations, AES-128/192 CBC, SHA/HMAC vectors, and failure-path checks.
