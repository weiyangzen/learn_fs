# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_alg.c

## Purpose

`crypto4xx_alg.c` implements CryptoAPI algorithm operations for the AMCC/PPC4xx crypto engine. It builds dynamic Security Associations for AES ECB/CBC/CTR/RFC3686 and AEAD CCM/GCM, invokes packet-descriptor submission in the core file, and uses software fallbacks for hardware edge cases.

## Important APIs, Types, And Functions

Key helpers are `set_dynamic_sa_command_0()`, `set_dynamic_sa_command_1()`, `crypto4xx_crypt()`, `crypto4xx_setkey_aes()`, `crypto4xx_setkey_aes_{cbc,ecb,ctr}()`, `crypto4xx_setkey_rfc3686()`, `crypto4xx_ctr_crypt()`, `crypto4xx_aead_need_fallback()`, `crypto4xx_aead_fallback()`, `crypto4xx_setkey_aes_ccm()`, `crypto4xx_crypt_aes_ccm()`, `crypto4xx_setkey_aes_gcm()`, and `crypto4xx_crypt_aes_gcm()`.

## Control Flow

Setkey routines allocate inbound/outbound SA buffers, fill command words, key fields, key lengths, mode bits, and AEAD hash state. Encrypt/decrypt entry points build IV words, choose inbound or outbound SA, and call `crypto4xx_build_pd()`. CTR falls back if the 32-bit hardware counter would overflow while Linux expects full-IV carry. AEAD falls back when auth size is not word aligned, plaintext is shorter than one AES block, associated data is unaligned or over 1020 bytes, or CCM counter length is unsupported.

## State And Persistence Behavior

TFM state is in `struct crypto4xx_ctx`: device pointer, inbound/outbound SA buffers, SA length, RFC3686 nonce, and fallback cipher/AEAD. Per-request state is mostly supplied to the core packet descriptor builder. GCM computes the GHASH subkey in software during setkey and stores it inside the SA.

## Dependencies And Integration Points

It depends on `crypto4xx_core.c` for descriptor submission, `crypto4xx_sa.h` for dynamic SA layout, `crypto4xx_core.h` endian-copy helpers, AES/CTR/GCM/AEAD CryptoAPI headers, and fallback algorithms configured by core algorithm registration.

## Risks And Test Signals

Risks include SA bitfield mistakes, endian conversion errors in key/IV/hash subkey fields, AEAD fallback boundary regressions, CCM nonce-length handling, auth tag placement/checking across core completion, and use of stack temporary SAs in asynchronous submission. Test AES mode vectors, RFC3686 nonce handling, CTR overflow fallback, CCM/GCM vectors with multiple auth sizes and assoc lengths, short plaintext fallback, and key-size rejection.
