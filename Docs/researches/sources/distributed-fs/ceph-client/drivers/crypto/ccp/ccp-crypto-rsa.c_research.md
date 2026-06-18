# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-rsa.c

## Purpose

`ccp-crypto-rsa.c` implements Crypto API `rsa` akcipher offload using the CCP RSA engine. It parses public/private keys, stores modulus/exponent/private exponent in scatterlists, builds RSA commands for encrypt/decrypt operations, updates output length on completion, and registers version-gated RSA support.

## Important APIs, Types, And Functions

- `akcipher_request_cast()` converts async requests to akcipher requests.
- `ccp_copy_and_save_keypart()` strips leading zero bytes from key parts, records resulting length, and duplicates the data.
- `ccp_rsa_complete()` sets `req->dst_len` from hardware key size on success.
- `ccp_rsa_maxsize()` returns modulus length.
- `ccp_rsa_crypt()` fills a `CCP_ENGINE_RSA` command using public exponent for encrypt or private exponent for decrypt.
- `ccp_check_key_length()` restricts modulus size to 8..4096 bits at this layer.
- `ccp_rsa_free_key_bufs()` frees sensitive key buffers and clears pointers/lengths.
- `ccp_rsa_setkey()` parses ASN.1 public/private keys, stores n/e/d, initializes SGs, and validates key length.
- `ccp_rsa_init_tfm()` and `ccp_rsa_exit_tfm()` set request size/completion and free key material.
- `ccp_register_rsa_algs()` registers `rsa` for CCP v3 and later.

## Control Flow

Setting a key first frees any old key material. It parses either private or public RSA key data using shared kernel RSA parsers, strips leading zeroes from modulus and exponent parts, initializes scatterlists, computes bit length, and validates it. Private-key setup additionally stores `d`.

Encrypt/decrypt requests create a command with key size in bits, exponent SG selected by operation, modulus SG, source length, and destination SG, then enqueue through the shared CCP crypto queue. Completion sets the destination length to the key size in bytes if the lower command succeeded.

## State And Persistence Behavior

Transform state stores allocated sensitive buffers for `n`, `e`, and optional `d`, their SG wrappers, byte lengths, and key length in bits. Buffers are freed with `kfree_sensitive()` on replacement and transform exit. Request state contains only the command wrapper.

## Dependencies And Integration Points

This file depends on Crypto API akcipher/RSA parsers, scatterlists, `ccp-crypto.h`, `ccp_version()`, and `ccp_crypto_enqueue_request()`. Lower CCP operation code must implement `CCP_ENGINE_RSA` for the active hardware version.

## Risks And Edge Cases

- The local key length limit is 4096 bits even though v5 device data exposes a wider `CCP5_RSA_MAX_WIDTH`; this provider does not use that larger limit.
- Public-key transforms lack `d`; calling decrypt without a private key would submit an uninitialized/empty private exponent unless higher layers prevent that usage.
- RSA here is raw modular exponentiation exposed through akcipher; padding schemes are handled elsewhere or by callers.
- Leading-zero stripping changes buffer lengths; hardware key-size handling must still align source/destination widths correctly.

## Test Signals

Signals include RSA encrypt/decrypt known-answer tests, public/private key parsing, leading-zero modulus/exponent keys, key size boundary rejection, max output length reporting, sensitive buffer cleanup on key replacement, and v3/v5 registration tests.
