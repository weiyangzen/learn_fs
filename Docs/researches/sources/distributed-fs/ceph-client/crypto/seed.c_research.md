# sources/distributed-fs/ceph-client/crypto/seed.c

Purpose: implements the SEED 128-bit block cipher as a legacy `cipher` crypto algorithm.

Important APIs, types, and functions: `struct seed_ctx` stores a 32-word key schedule. `seed_set_key()` expands the 16-byte key using KISA constants and SS tables. `seed_encrypt()` and `seed_decrypt()` run 16 Feistel rounds using the `OP` macro. The algorithm registers as `seed`/`seed-generic`.

Control flow: setkey reads four big-endian 32-bit key words, iterates 16 key-constant rounds, writes two subkeys per round, and rotates word pairs alternately. Encryption reads a 16-byte block as big-endian words, applies the round function in increasing key order, swaps halves in the final output, and writes big-endian output. Decryption uses the same round function in reverse subkey order.

State and persistence: expanded subkeys persist in the tfm context until the tfm is freed or rekeyed. No request-level state is retained by the block cipher primitive.

Dependencies and integration points: uses unaligned big-endian helpers and registers through the legacy `crypto_alg` cipher interface. Modes such as ECB/CBC can wrap it through crypto templates.

Risks: SEED is regionally standardized and legacy; new protocols normally use AES or modern AEADs. Large S-box tables and macro round logic are sensitive to transcription errors. The code assumes the crypto API enforces the 16-byte key length declared in algorithm metadata.

Test signals: RFC 4269/KISA known-answer vectors, encrypt/decrypt inverse tests, mode-template wrapping, unaligned input/output buffers, and module alias lookup.
