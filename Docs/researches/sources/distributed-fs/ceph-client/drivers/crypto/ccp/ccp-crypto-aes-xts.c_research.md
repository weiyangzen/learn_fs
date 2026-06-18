# sources/distributed-fs/ceph-client/drivers/crypto/ccp/ccp-crypto-aes-xts.c

## Purpose

`ccp-crypto-aes-xts.c` provides the Crypto API `xts(aes)` skcipher backed by CCP XTS-AES hardware when the request fits hardware constraints, with a software fallback for unsupported unit sizes or key sizes. It registers the algorithm, manages fallback transform lifetime, validates XTS keys, and updates IV/tweak output on hardware completion.

## Important APIs, Types, And Functions

- `aes_xts_algs[]` names the registered algorithm and driver.
- `xts_unit_sizes[]` maps supported request lengths 16, 512, 1024, 2048, and 4096 to CCP unit-size encodings.
- `ccp_aes_xts_complete()` copies the updated IV/tweak from request context to `req->iv`.
- `ccp_aes_xts_setkey()` validates XTS keys, stores supported key material, sets hardware key length, initializes key SG, and sets the fallback transform key.
- `ccp_aes_xts_crypt()` chooses hardware or fallback path, fills a `CCP_ENGINE_XTS_AES_128` command for supported requests, and submits it.
- `ccp_aes_xts_init_tfm()` allocates fallback `xts(aes)` with `CRYPTO_ALG_NEED_FALLBACK` and sizes request context to include fallback request storage.
- `ccp_aes_xts_exit_tfm()` frees the fallback transform.
- `ccp_register_aes_xts_algs()` registers the algorithm.

## Control Flow

Requests first validate that a key has been set and an IV is present. The code searches for an exact request-length match in `xts_unit_sizes[]`. It forces fallback if no unit size matches, if v3 hardware is asked to use a non-AES-128 XTS key, or if the key half length is neither 128 nor 256 bits. Fallback requests reuse the caller callback/data and call the software skcipher directly. Hardware requests copy the IV, initialize its SG, populate the XTS command with action, unit size, key, IV, source/destination, and enqueue through the shared CCP crypto queue.

## State And Persistence Behavior

Transform state stores the fallback skcipher pointer, hardware key bytes, key length, and key SG. Request state stores IV, IV SG, CCP command, and embedded fallback request. The fallback transform persists for the tfm lifetime and is freed in exit.

## Dependencies And Integration Points

This file depends on Crypto API skcipher/XTS helpers, scatterwalk, CCP shared crypto header, `ccp_version()`, and `ccp_crypto_enqueue_request()`. It is registered as part of AES algorithm registration in `ccp-crypto-main.c`.

## Risks And Edge Cases

- Hardware is used only when `cryptlen` exactly equals a supported unit size, even though hardware may support multiples; larger valid XTS requests fall back.
- `ccp_aes_xts_setkey()` sets `key_len` even if AES-256 on v3 did not copy hardware key material; later v3 requests should fallback because of version/key checks.
- Fallback request storage must remain last in `ccp_aes_req_ctx`; the header comments rely on that for variable request size.
- The source comment says "bug" where it means "but"; maintainers should read the block as a hardware/software limitation note, not a known defect marker.

## Test Signals

Signals include XTS known-answer tests for 16/512/1024/2048/4096-byte requests on v5 hardware, fallback coverage for odd sizes and unsupported v3 AES-256, key verification failures for weak/equal halves, IV update correctness, and module unload freeing fallback tfms.
