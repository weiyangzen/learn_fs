# sources/distributed-fs/ceph-client/arch/x86/crypto/blowfish_glue.c

Purpose: Linux crypto API glue for the x86_64 optimized Blowfish implementation. It registers the base cipher and ECB/CBC skcipher variants and routes bulk work to scalar or 4-way assembly.

Important APIs/types/functions: declares assembly entry points, wraps 4-way decrypt into `blowfish_dec_ecb_4way` and `blowfish_dec_cbc_4way`, implements `blowfish_encrypt`, `blowfish_decrypt`, `blowfish_setkey_skcipher`, ECB/CBC request handlers, `is_blacklisted_cpu`, and module init/exit. Registers `blowfish-asm`, `ecb-blowfish-asm`, and `cbc-blowfish-asm`.

Control flow: ECB encrypt/decrypt walkers use 4-way blocks where possible and scalar blocks for tails. CBC encrypt is inherently serial and uses scalar encryption. CBC decrypt can process 4 blocks in parallel because each plaintext block is the decrypted ciphertext XORed with the previous ciphertext block. Module init rejects Pentium 4 unless `force` is set, then registers the cipher algorithm first and skciphers second, rolling back on failure.

State and persistence: key schedule state lives per transform in `struct bf_ctx`. Module-global state is the `force` parameter and registered algorithm metadata. No on-disk or cross-request persistence exists.

Dependencies and integration points: depends on generic `blowfish_setkey`, crypto alg/skcipher registration, and `ecb_cbc_helpers.h`. It provides higher-priority skcipher drivers than generic implementations and a base cipher driver for users of `crypto_cipher`.

Risks: registration rollback unregisters the base cipher if skcipher registration fails, but exit unregisters both unconditionally in normal loaded state. Performance blacklist must be kept architecture-specific. CBC decrypt correctness depends on helper macro ordering and the assembly `cbc` flag.

Test signals: crypto selftests for Blowfish key sizes, ECB/CBC encrypt/decrypt, odd block counts, in-place operation, registration failure injection if available, and blacklisted CPU path with and without `force`.
