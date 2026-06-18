# sources/distributed-fs/ceph-client/net/mac80211/wep.c

## Purpose
`wep.c` implements mac80211 software WEP encryption/decryption and IV insertion/removal. It supports both full software crypto and hardware-assisted cases where mac80211 only reserves or generates IV space.

## Important APIs, Types, And Functions
Public entry points are `ieee80211_wep_init()`, `ieee80211_wep_encrypt_data()`, `ieee80211_wep_encrypt()`, `ieee80211_wep_decrypt_data()`, `ieee80211_crypto_wep_decrypt()`, and `ieee80211_crypto_wep_encrypt()`. Internal helpers include `ieee80211_wep_weak_iv()`, `ieee80211_wep_get_iv()`, `ieee80211_wep_add_iv()`, `ieee80211_wep_remove_iv()`, `ieee80211_wep_decrypt()`, and `wep_encrypt_skb()`. It uses `struct arc4_ctx`, `struct ieee80211_key`, TX/RX data wrappers, and skb head/tail manipulation.

## Control Flow
Initialization seeds `local->wep_iv` randomly. TX flow sets the Protected bit on all skbs, then either performs full software WEP or inserts IV/IV space for hardware. Software encryption inserts a 4-byte IV after the 802.11 header, skips weak RC4 IVs, appends a 4-byte ICV, builds RC4 key material as IV plus secret key, CRC32s the plaintext, and ARC4-encrypts payload plus ICV.

RX flow only handles data and authentication frames. If hardware did not decrypt, it linearizes the skb, validates the Protected bit and frame length, checks key index, builds the RC4 key from the received IV and key, decrypts payload plus ICV, validates CRC32, trims ICV, and removes IV. If hardware decrypted but did not strip IV/ICV, it removes those fields according to RX flags.

## State And Persistence
State is runtime only. `local->wep_iv` monotonically changes for TX IV generation. `local->wep_tx_ctx` and `local->wep_rx_ctx` are temporary ARC4 contexts zeroed after use. The skb is modified in place by pushing IVs, appending/trimming ICVs, and moving headers.

## Dependencies And Integration Points
The file depends on CRC32, ARC4, random bytes, unaligned access, skb helpers, `ieee80211_i.h`, and key definitions. It integrates with the mac80211 TX/RX crypto handler chain, shared-key authentication frame construction in `util.c`, hardware key flags such as `GENERATE_IV` and `PUT_IV_SPACE`, and RX status flags such as `DECRYPTED`, `IV_STRIPPED`, and `ICV_STRIPPED`.

## Risks And Edge Cases
WEP is cryptographically obsolete; this code is compatibility support. Correct headroom/tailroom is mandatory, with failures causing TX drops. Weak-IV skipping only handles known FMS-style weak IVs and does not make WEP secure. RX removes IV/ICV even when software ICV verification fails, so callers must drop on the returned failure. Hardware flag combinations must match actual driver behavior or IV/ICV fields can be duplicated or left in payload.

## Test Signals
Test signals include known-answer WEP encrypt/decrypt vectors, weak-IV skip behavior, key-index mismatch drops, short frame drops, hardware-decrypted IV/ICV stripping combinations, shared-key auth transaction encryption, and skb headroom/tailroom failure paths.
