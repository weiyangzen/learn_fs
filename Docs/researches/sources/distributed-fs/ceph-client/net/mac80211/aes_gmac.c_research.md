# sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.c

Purpose: this file implements AES-GMAC MIC generation/verification support for IEEE 802.11 BIP-GMAC-128 and BIP-GMAC-256 management frame protection. It uses the kernel AEAD GCM transform as a GMAC engine by encrypting/authenticating with zero plaintext length and all relevant frame bytes as associated data.

Important APIs: `ieee80211_aes_gmac()` computes the GMAC tag using a configured `struct crypto_aead`, 20-byte WLAN AAD, 12-byte nonce, frame data, frame length, and MIC buffer. `ieee80211_aes_gmac_key_setup()` allocates `gcm(aes)`, sets the key and `IEEE80211_GMAC_MIC_LEN` authsize, and returns the transform or `ERR_PTR`. `ieee80211_aes_gmac_key_free()` releases the transform.

Control flow: `ieee80211_aes_gmac()` rejects frames shorter than the GMAC MIC length. It allocates one sensitive block holding the AEAD request, a zero buffer the size of the MIC, and a copied AAD. For beacon frames, it builds a five-entry scatterlist: AAD, eight zero bytes replacing Timestamp, the post-timestamp frame body excluding MIC, zeroed MIC field, and output MIC. For other frames, it uses AAD, frame body excluding MIC, zeroed MIC field, and output MIC. It builds a 16-byte GCM IV from the 12-byte nonce plus zeros and counter byte `0x01`, sets crypt length to zero, marks associated data as `GMAC_AAD_LEN + data_len`, and calls `crypto_aead_encrypt()`.

State and persistence behavior: per-call AEAD request state is transient and allocated with `GFP_ATOMIC`; key state persists in the transform. The copied AAD and zero region are freed with `kfree_sensitive()` to avoid retaining authentication material.

Dependencies and integration: it depends on Crypto API AEAD/GCM, AES block sizing, mac80211 frame helpers, `key.h`, and `aes_gmac.h`. Key setup/free is used in `key.c`; MIC calculation is used by `wpa.c` BIP-GMAC TX/RX paths and error counters in key/debugfs paths.

Risks: scatterlist associated-data length must exactly match the 802.11 BIP-GMAC calculation, including zeroing the beacon Timestamp and MIC field. Any caller that passes a too-short beacon body could underflow the `data_len - 8 - MIC` calculation; frame validation before this helper is therefore critical. As with `aead_api.c`, async transform behavior is not explicitly waited on.

Test signals: BIP-GMAC-128/256 known-answer tests should include beacon and non-beacon frames. RX tests should exercise replay and MIC failures; TX tests should verify nonce construction and produced MMIE tags.
