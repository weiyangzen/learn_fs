# sources/distributed-fs/ceph-client/net/mac80211/wpa.h

## Purpose
`wpa.h` declares the internal mac80211 WPA/TKIP/CCMP/GCMP/BIP TX and RX crypto handler interface implemented by `wpa.c`.

## Important APIs, Types, And Functions
It declares handler functions for Michael MIC, TKIP, CCMP, AES-CMAC BIP, AES-GMAC BIP, and GCMP: `ieee80211_tx_h_michael_mic_add()`, `ieee80211_rx_h_michael_mic_verify()`, `ieee80211_crypto_tkip_encrypt()`, `ieee80211_crypto_tkip_decrypt()`, `ieee80211_crypto_ccmp_encrypt()`, `ieee80211_crypto_ccmp_decrypt()`, `ieee80211_crypto_aes_cmac_encrypt()`, `ieee80211_crypto_aes_cmac_decrypt()`, `ieee80211_crypto_aes_gmac_encrypt()`, `ieee80211_crypto_aes_gmac_decrypt()`, `ieee80211_crypto_gcmp_encrypt()`, and `ieee80211_crypto_gcmp_decrypt()`.

## Control Flow
The header has no control flow. The TX/RX handler pipeline includes these functions depending on selected cipher and frame type.

## State And Persistence
No state is stored in the header. Declared functions operate on runtime `struct ieee80211_tx_data`, `struct ieee80211_rx_data`, keys, stations, and skbs.

## Dependencies And Integration Points
The header includes Linux skb/types and `ieee80211_i.h`. It is consumed by mac80211 crypto/TX/RX orchestration code that selects cipher-specific handlers.

## Risks And Edge Cases
Callers must pass handlers only when `tx->key`/`rx->key` and cipher context are suitable. The `mic_len` arguments for CCMP and AES-CMAC must match the cipher variant or frame parsing/trimming will be wrong.

## Test Signals
Compilation plus cipher-specific TX/RX tests in `wpa.c` consumers provide coverage.
