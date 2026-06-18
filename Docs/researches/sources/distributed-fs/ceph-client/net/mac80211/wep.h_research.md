# sources/distributed-fs/ceph-client/net/mac80211/wep.h

## Purpose
`wep.h` declares the internal mac80211 WEP software crypto interface used by TX/RX handlers and authentication-frame helpers.

## Important APIs, Types, And Functions
It exposes `ieee80211_wep_init()`, raw data helpers `ieee80211_wep_encrypt_data()` and `ieee80211_wep_decrypt_data()`, skb-level `ieee80211_wep_encrypt()`, and handler entry points `ieee80211_crypto_wep_decrypt()` and `ieee80211_crypto_wep_encrypt()`. It includes `ieee80211_i.h` and `key.h`, so callers see `struct ieee80211_local`, `struct ieee80211_key`, `struct ieee80211_rx_data`, and `struct ieee80211_tx_data`.

## Control Flow
The header has no control flow. It separates WEP implementation details in `wep.c` from callers in the broader mac80211 TX/RX and management-frame code.

## State And Persistence
No state is stored in the header. Declared functions operate on runtime mac80211 local/key/TX/RX state and mutate skbs.

## Dependencies And Integration Points
This header is included by `wep.c` and other mac80211 files that need WEP helpers, notably authentication frame construction and TX/RX crypto handler setup. It depends on skb and Linux integer types.

## Risks And Edge Cases
Because the header exposes low-level raw data helpers, callers must pass correctly sized buffers with ICV tailroom and correct RC4 key material. Misuse bypasses skb-level IV/key-index validation.

## Test Signals
Compilation coverage is the primary header-level signal. Functional coverage comes from WEP TX/RX tests and callers using `ieee80211_wep_encrypt()` for shared-key authentication.
