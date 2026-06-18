# sources/distributed-fs/ceph-client/net/mac80211/aes_ccm.h

Purpose: this header provides inline AES-CCM helpers for mac80211 CCMP-style protection. It adapts WLAN-specific AAD layout to the generic AEAD helper interface in `aead_api.h`.

Important APIs: `CCM_AAD_LEN` is defined as 32, matching the maximum WLAN CCMP AAD workspace. `ieee80211_aes_key_setup_encrypt()` creates a `ccm(aes)` transform with caller-supplied key length and MIC length. `ieee80211_aes_ccm_encrypt()` and `ieee80211_aes_ccm_decrypt()` pass `b_0`, the AAD payload after its two-byte length prefix, the parsed big-endian AAD length, the data buffer, and the MIC buffer to the generic AEAD helpers. `ieee80211_aes_key_free()` releases the transform.

Control flow and data contract: the most important behavior is the AAD convention. Callers pass an AAD buffer whose first two bytes contain the big-endian AAD length, followed by the actual AAD bytes. The inline wrappers skip the prefix (`aad + 2`) and compute `aad_len` with `be16_to_cpup((__be16 *)aad)`. The same convention is used for both encryption and decryption. The payload buffer is encrypted/decrypted in place by the lower helper.

State and persistence behavior: no local state exists in this header. Persistent state is the `struct crypto_aead` transform created for each key and owned by mac80211 key state.

Dependencies and integration: this header depends on `aead_api.h`, endian helpers available in kernel headers, and Crypto API transform semantics. It is included by `key.c` for CCMP key setup/free and `wpa.c` for CCMP encryption/decryption.

Risks: the wrapper assumes the two-byte AAD length prefix is present and valid; malformed caller buffers can produce wrong authentication input. The function name `ieee80211_aes_key_setup_encrypt()` is generic despite selecting CCM, so nearby code must avoid confusing it with GCM/GMAC setup names. MIC length is caller-configurable, which is required for CCMP variants but must match the cipher suite.

Test signals: CCMP and CCMP-256 known-answer tests, association traffic protected by CCMP, and negative MIC tests should exercise these wrappers. Static build coverage should include all CCMP key lengths and MIC sizes used by mac80211.
