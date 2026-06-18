# sources/distributed-fs/ceph-client/arch/x86/crypto/camellia_glue.c

Purpose: Baseline x86_64 Camellia glue and key schedule implementation. It exports scalar/2-way assembly symbols, S-box tables, key expansion, CBC helper logic, and crypto API registrations.

Important APIs/types/functions: exports `__camellia_enc_blk`, `camellia_dec_blk`, `__camellia_enc_blk_2way`, `camellia_dec_blk_2way`, `__camellia_setkey`, and `camellia_decrypt_cbc_2way`. Contains eight 256-entry S-box tables, sigma constants, `camellia_setup128`, `camellia_setup192`, `camellia_setup256`, `camellia_setup_tail`, and crypto callbacks for cipher/ECB/CBC registration.

Control flow: key setup validates 16/24/32-byte keys, records `key_length`, builds KL/KR/KA/KB-derived subkeys with rotations and Camellia F-functions, and reshapes subkeys for assembly consumption. Request handlers use 2-way blocks for ECB and CBC decrypt where possible, scalar for tails, and scalar CBC encryption. Module init blacklists Pentium 4 unless `force` is set, registers the base cipher, then skciphers with rollback on failure.

State and persistence: per-transform persistent state is `struct camellia_ctx` containing expanded key material and key length. S-box tables are read-only globals visible to assembly. Module-global mutable state is the `force` parameter and registration state only.

Dependencies and integration points: uses Linux unaligned big-endian loads, crypto registration APIs, `ecb_cbc_helpers.h`, and the scalar assembly file. Exports are reused by AVX and AVX2 modules for tails and shared key setup.

Risks: key expansion is dense and feeds hand-written assembly; subkey ordering bugs affect every optimized Camellia driver. `camellia_decrypt_cbc_2way` has explicit in-place handling by copying the IV block when needed. Blacklist logic is performance-driven and should not hide functional regressions.

Test signals: known-answer tests for all key sizes, raw cipher API, ECB/CBC skcipher API, invalid key lengths, 2-way CBC decrypt in-place, module registration rollback, and AVX/AVX2 tail reuse all exercise this file.
