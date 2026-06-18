# sources/distributed-fs/ceph-client/net/mac80211/aead_api.c

Purpose: this file is a small mac80211 wrapper around the kernel Crypto API AEAD interface. It centralizes common authenticated encryption/decryption setup for CCM and GCM based WLAN ciphers, including scatterlist construction, AEAD request allocation, associated-data handling, MIC placement, key setup, and transform teardown.

Important APIs: `aead_encrypt()` builds a three-entry scatterlist of AAD, payload, and MIC output, sets the IV/nonce pointer from `b_0`, marks the AAD length with `aead_request_set_ad()`, and calls `crypto_aead_encrypt()`. `aead_decrypt()` mirrors the setup but includes `data_len + mic_len` in the crypt length and rejects `data_len == 0` with `-EINVAL`. `aead_key_setup_encrypt()` allocates a `struct crypto_aead` by algorithm name, sets the raw key, sets the authentication tag length, and returns either the transform or an `ERR_PTR`. `aead_key_free()` calls `crypto_free_aead()`.

Control flow: each operation computes `mic_len` from `crypto_aead_authsize(tfm)` and `reqsize` from the transform-specific request size. A single allocation holds the `aead_request` and a copied AAD buffer. The AAD copy is important because the request scatterlist points into allocation-owned memory while the crypto call runs. Encryption writes the authentication tag through the MIC scatterlist element; decryption authenticates the tag supplied in that element. Both paths scrub request memory with `kfree_sensitive()` before returning.

State and persistence behavior: the per-operation request allocation is transient and uses `GFP_ATOMIC`, so callers may use it in atomic TX/RX crypto contexts. Persistent crypto state lives in the `struct crypto_aead` transform returned by `aead_key_setup_encrypt()` and is owned by mac80211 key state until `aead_key_free()`.

Dependencies and integration: the file depends on `<crypto/aead.h>`, scatterlists, Linux error-pointer conventions, and `aead_api.h`. `aes_ccm.h` and `aes_gcm.h` inline wrappers call these helpers with `ccm(aes)` and `gcm(aes)`. Higher-level users are WPA/GCMP/CCMP paths in `wpa.c` and key allocation/freeing in `key.c`.

Risks: incorrect AAD length, nonce block format, or MIC length from callers produces authentication failures. The helpers assume synchronous completion even though transforms are allocated with `CRYPTO_ALG_ASYNC`; if an async provider returned `-EINPROGRESS` without caller completion handling, the current stack would not wait. Allocation with `GFP_ATOMIC` can fail under pressure, so callers must propagate `-ENOMEM`.

Test signals: CCMP/GCMP encrypt/decrypt known-answer tests, replay/MIC failure tests in WPA receive paths, and fault injection for `kzalloc()` and `crypto_aead_setkey()` failures are useful. Runtime signals include successful association with CCMP/GCMP networks and absence of MIC/authentication errors under load.
