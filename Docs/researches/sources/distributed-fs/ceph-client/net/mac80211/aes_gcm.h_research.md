# sources/distributed-fs/ceph-client/net/mac80211/aes_gcm.h

Purpose: this header provides inline AES-GCM helpers for GCMP and GCMP-256 data protection in mac80211. It maps WLAN AAD layout and GCMP MIC sizing onto the shared AEAD helper implementation.

Important APIs: `GCM_AAD_LEN` is defined as 32. `ieee80211_aes_gcm_encrypt()` and `ieee80211_aes_gcm_decrypt()` pass the GCM initial counter block `j_0`, AAD after the two-byte length prefix, the parsed AAD length, payload, and MIC buffer to `aead_encrypt()`/`aead_decrypt()`. `ieee80211_aes_gcm_key_setup_encrypt()` creates a `gcm(aes)` AEAD transform using `IEEE80211_GCMP_MIC_LEN` as the authsize. `ieee80211_aes_gcm_key_free()` releases it.

Control flow and data contract: like `aes_ccm.h`, the wrapper assumes the caller supplied a two-byte big-endian AAD length prefix. The wrapper does not construct `j_0`; GCMP code in `wpa.c` is responsible for nonce/counter block construction. Encryption and decryption operate in place on the data buffer, with the authentication tag supplied separately as `mic`.

State and persistence behavior: no state is held in this header. A configured `struct crypto_aead` transform persists in the mac80211 key object until freed.

Dependencies and integration: it includes `aead_api.h`, relies on `IEEE80211_GCMP_MIC_LEN` from mac80211 headers available to consumers, and integrates with `key.c` for transform allocation/free plus `wpa.c` for GCMP frame processing.

Risks: the wrapper hardcodes the GCMP MIC length, so alternate suites must match `IEEE80211_GCMP_MIC_LEN`. Incorrect AAD prefix, `j_0` construction, or key length causes authentication failures. As with other AEAD helpers, async Crypto API completion assumptions should be watched if providers change.

Test signals: GCMP and GCMP-256 known-answer tests, real encrypted data traffic, replay rejection, MIC failure accounting, and failure injection around transform allocation are the primary signals.
