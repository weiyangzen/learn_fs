# sources/distributed-fs/ceph-client/net/mac80211/aead_api.h

Purpose: this header declares the shared AEAD helper interface used by mac80211 cipher-specific wrappers. It hides kernel Crypto API request setup details from `aes_ccm.h` and `aes_gcm.h`, while still exposing transform ownership explicitly through `struct crypto_aead *`.

Important APIs and types: `aead_key_setup_encrypt(const char *alg, const u8 key[], size_t key_len, size_t mic_len)` creates and configures an AEAD transform. `aead_encrypt()` and `aead_decrypt()` accept a transform, nonce/control block pointer, associated data pointer and length, mutable data buffer, payload length, and MIC buffer. `aead_key_free()` releases the transform. The header includes `<crypto/aead.h>` and `<linux/crypto.h>`, so users can name `struct crypto_aead` and Crypto API constants.

Control flow: the header itself has no execution flow, but it defines the call contract used by inline cipher wrappers. Callers are responsible for formatting the nonce block (`b_0` for CCM or `j_0` for GCM), passing the correct AAD start pointer and length, and allocating a MIC buffer whose size matches the transform authsize configured at setup.

State and persistence behavior: state is represented only by the opaque `struct crypto_aead` pointer. The header does not prescribe storage, but in mac80211 the transform is normally stored in key-specific state and freed when the key is destroyed.

Dependencies and integration: `aes_ccm.h` and `aes_gcm.h` are the direct consumers. The implementation in `aead_api.c` relies on Linux scatterlists, error pointers, AEAD requests, and sensitive-memory free semantics. Higher-level integration reaches `key.c` and `wpa.c` through the cipher-specific headers.

Risks: the interface is low level and trusts callers on buffer lengths and nonce/AAD format. Passing stack or transient buffers is okay because the implementation copies AAD, but data and MIC buffers are used in place. Misconfigured `mic_len` at setup time affects every later encrypt/decrypt operation on that transform.

Test signals: build coverage catches prototype mismatches. Runtime crypto tests should validate both header consumers, including CCMP and GCMP key setup, encryption, decryption, and negative authentication cases.
