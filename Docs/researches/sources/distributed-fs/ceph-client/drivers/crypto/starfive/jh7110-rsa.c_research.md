# sources/distributed-fs/ceph-client/drivers/crypto/starfive/jh7110-rsa.c

## Purpose

This file implements RSA public-key acceleration for the StarFive JH7110 crypto block. It exposes the kernel `akcipher` algorithm name `rsa` with driver name `starfive-rsa`, parses public and private RSA keys, uses the hardware PKA registers for modular exponentiation in Montgomery form, and falls back to `rsa-generic` when no suitable hardware key is installed.

## Important APIs, types, and functions

The PKA register interface uses offsets under `STARFIVE_PKA_REGS_OFFSET`: control/status (`CACR`, `CASR`), operand/result (`CAAR`), exponent (`CAER`), and modulus (`CANR`). The command constants describe Montgomery preprocessing and multiply/exponent operations: `CRYPTO_CMD_PRE`, `CRYPTO_CMD_ARN`, `CRYPTO_CMD_AERN`, and `CRYPTO_CMD_AARN`. `starfive_pka_wait_done()` polls `STARFIVE_PKA_DONE`. Key lifetime is managed by `starfive_rsa_free_key()`, `starfive_rsa_set_n()`, `starfive_rsa_set_e()`, `starfive_rsa_set_d()`, and `starfive_rsa_setkey()`.

The core math path is `starfive_rsa_montgomery_form()` and `starfive_rsa_cpu_start()`. The latter converts the message into Montgomery form, writes it as the active operand, performs square-and-multiply over exponent bits from `starfive_rsa_get_nbit()`, reads the result, and converts out of Montgomery form. `starfive_rsa_enc_core()` copies request data from sg into an aligned buffer, selects public exponent or private exponent, invokes the PKA path, copies the result to the destination sg, and resets the PKA block. `starfive_rsa_enc()` and `starfive_rsa_dec()` implement akcipher encrypt/decrypt entry points.

## Control flow, state, and persistence

Transform initialization finds the shared StarFive crypto device, allocates a `rsa-generic` fallback, and sets an akcipher request size. `set_pub_key` and `set_priv_key` first configure the fallback, then parse DER-encoded RSA keys through `rsa_parse_pub_key()` or `rsa_parse_priv_key()`. If the modulus is larger than the hardware maximum plus one possible leading-zero byte, the StarFive key is left empty so subsequent operations use the fallback. Otherwise, modulus, exponent, and optional private exponent are stored right-aligned in `struct starfive_rsa_key` with bit lengths derived from the first nonzero byte.

Encrypt/decrypt requests validate that the required key components are present and that `dst_len` can hold the modulus-sized result. The hardware path is synchronous: it resets PKA, pads unaligned input at the front of `rctx->rsa_data`, copies from source sg, executes modular exponentiation, copies exactly `key_sz` bytes to destination sg, then resets PKA again. Persistent state is limited to per-transform key buffers and the fallback transform; all request buffers and PKA register contents are transient.

## Dependencies and integration points

The file depends on the kernel akcipher API, RSA key parsers from `crypto/internal/rsa.h`, scatterlist copy helpers, MMIO polling, and shared StarFive crypto structures from `jh7110-cryp.h`. `starfive_rsa_register_algs()` and `starfive_rsa_unregister_algs()` are the parent-driver hooks. The algorithm advertises `CRYPTO_ALG_NEED_FALLBACK` and priority 3000, so it participates in normal crypto API lookup while retaining `rsa-generic` for unsupported key sizes or pre-key operations.

## Risks and test signals

Risks cluster around endian/layout assumptions for operand arrays, leading-zero key normalization, modulus-size limits, front-padding of non-word-aligned input, and the hand-written square-and-multiply loop. The operation is synchronous and polls up to 100 ms per PKA command, so large exponents can create latency under crypto API callers. There is no blinding in this hardware path, which matters for private-key side-channel review. Test signals include RSA selftests for public and private keys at supported sizes, leading-zero modulus encodings, fallback behavior for oversized keys, insufficient `dst_len` returning `-EOVERFLOW`, unaligned source lengths, and repeated encrypt/decrypt cycles verifying that PKA reset leaves later requests independent.
