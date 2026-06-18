# sources/distributed-fs/ceph-client/net/mac80211/aes_gmac.h

Purpose: this header declares the AES-GMAC interface used by mac80211 BIP-GMAC management protection paths. It exposes GMAC-specific AAD and nonce lengths and the three transform/MIC helper functions implemented in `aes_gmac.c`.

Important APIs and constants: `GMAC_AAD_LEN` is 20 bytes and `GMAC_NONCE_LEN` is 12 bytes. `ieee80211_aes_gmac_key_setup()` creates a key-specific `gcm(aes)` AEAD transform. `ieee80211_aes_gmac()` computes or verifies the GMAC tag over WLAN AAD and frame data, depending on caller comparison. `ieee80211_aes_gmac_key_free()` releases the transform.

Control flow and contract: callers must prepare the 20-byte AAD, 12-byte nonce, frame data including a trailing MIC field, and MIC output/comparison buffer. The implementation treats frame data as associated data and writes a GMAC tag into `mic`.

State and persistence behavior: no local state is declared. The `struct crypto_aead` pointer returned by setup is persistent key state and must be freed on key destruction.

Dependencies and integration: it includes `<linux/crypto.h>` for Crypto API types. It is consumed by `key.c` for BIP-GMAC key lifecycle and `wpa.c` for protected management frame processing.

Risks: the interface cannot enforce nonce uniqueness, frame length validity, or correct AAD construction. Those invariants are security-critical and live in callers. Compile-time constants reduce accidental length drift between setup and use.

Test signals: build coverage for BIP-GMAC suites, known-answer MIC tests, nonce/replay tests, and association tests using protected management frames with GMAC suites.
