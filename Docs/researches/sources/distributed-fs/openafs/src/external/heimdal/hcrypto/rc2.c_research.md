# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rc2.c

Purpose: implements RC2 key expansion, block encrypt/decrypt, and CBC mode for legacy compatibility.

Important APIs/types/functions: `RC2_set_key` expands caller key bytes into 64 16-bit words with effective-bit control; `RC2_encryptc` and `RC2_decryptc` process one 8-byte block; `RC2_cbc_encrypt` handles CBC encryption/decryption and partial trailing blocks.

Control flow: key setup clamps key length to 128 bytes and effective bits to 1024, expands through the RC2 S-box, applies the effective-key-bit mask, and fills `RC2_KEY`. Encryption loads four little-endian words, runs 16 mixing rounds with mash steps after rounds 4 and 10, and writes little-endian output. Decryption reverses that sequence. CBC encryption XORs plaintext with IV, encrypts, and updates IV; trailing partial encryption fills missing bytes from IV. CBC decryption saves ciphertext as next IV, decrypts, XORs output with previous IV, and handles partial output.

State and persistence: `RC2_KEY` stores expanded key data. CBC calls mutate the caller-provided IV in place.

Dependencies and integration points: depends on `rc2.h` and is exposed through EVP RC2 provider descriptors.

Risks and test signals: RC2 is legacy and should be compatibility-only. `RC2_set_key` aborts on nonpositive key length, partial CBC behavior is nonstandard for many protocols, and IV mutation must be expected by callers. Tests should cover RFC 2268 vectors, 40/64/full effective bits, encrypt/decrypt inverse, CBC IV updates, and partial block handling.
