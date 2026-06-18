# sources/distributed-fs/ceph-client/net/mac80211/wpa.c

## Purpose
`wpa.c` implements mac80211 software WPA/WPA2/WPA3-era crypto handlers for TKIP Michael MIC, TKIP encryption/decryption, CCMP/GCMP data protection, and BIP AES-CMAC/AES-GMAC management frame protection. It also coordinates with hardware crypto offload by generating IV/MMIE space only when driver key flags require it.

## Important APIs, Types, And Functions
Public handler entry points are `ieee80211_tx_h_michael_mic_add()`, `ieee80211_rx_h_michael_mic_verify()`, `ieee80211_crypto_tkip_encrypt()`, `ieee80211_crypto_tkip_decrypt()`, `ieee80211_crypto_ccmp_encrypt()`, `ieee80211_crypto_ccmp_decrypt()`, `ieee80211_crypto_gcmp_encrypt()`, `ieee80211_crypto_gcmp_decrypt()`, `ieee80211_crypto_aes_cmac_encrypt()`, `ieee80211_crypto_aes_cmac_decrypt()`, `ieee80211_crypto_aes_gmac_encrypt()`, and `ieee80211_crypto_aes_gmac_decrypt()`.

Internal helpers include `tkip_encrypt_skb()`, `ccmp_gcmp_aad()`, `ccmp_special_blocks()`, `ccmp_pn2hdr()`, `ccmp_hdr2pn()`, `gcmp_special_blocks()`, `gcmp_pn2hdr()`, `gcmp_hdr2pn()`, `bip_aad()`, `bip_ipn_set64()`, and `bip_ipn_swap()`. Important state lives in `struct ieee80211_key` cipher unions (`tkip`, `ccmp`, `gcmp`, `aes_cmac`, `aes_gmac`), atomic TX PN counters, RX PN replay windows, skb control blocks, and RX status flags.

## Control Flow
TKIP TX first adds a Michael MIC for data frames when needed, possibly forcing software crypto for injected MIC-failure tests. `tkip_encrypt_skb()` then inserts the TKIP IV, increments TX PN, optionally appends ICV, and either leaves encryption to hardware or calls TKIP software encryption. TKIP RX verifies/decrypts IV/ICV, updates per-security-index IV state, and separately verifies/removes Michael MIC or reports cfg80211 MIC failures.

CCMP/GCMP TX inserts an 8-byte header when software IV/space is needed, increments the atomic PN, writes PN to header format, builds AAD and nonce/special blocks, appends MIC for software crypto, and calls AES-CCM/AES-GCM helpers. RX validates frame type, header length, station presence, PN replay ordering unless hardware already validated it, decrypts/verifies MIC in software when needed, updates RX PN, stores fragment PN, then removes cipher header and MIC.

BIP TX appends MMIE, increments IPN, and computes AES-CMAC or AES-GMAC MIC over masked management header AAD plus frame body/MMIE unless hardware will generate the MMIE. BIP RX validates MMIE shape, checks IPN replay, verifies MIC when hardware did not, updates RX PN, and trims MMIE.

## State And Persistence
State is runtime key state only. TX uses `atomic64_inc_return(&key->conf.tx_pn)` for unique packet numbers. RX maintains per-key replay counters, MIC/ICV error counters, and latest accepted PN/IPN arrays. The skb is modified in place by pushing cipher headers, appending MIC/MMIE/ICV, trimming trailers, and moving 802.11 headers back over removed cipher headers.

## Dependencies And Integration Points
The file depends on TKIP, AES-CCM, AES-CMAC, AES-GMAC, AES-GCM helpers, crypto constant-time comparison, cfg80211 MIC failure reporting, RX drop reason enums, key flags, and mac80211 TX/RX handler sequencing. It integrates with hardware crypto via flags such as `GENERATE_IV`, `PUT_IV_SPACE`, `GENERATE_IV_MGMT`, `PUT_MIC_SPACE`, `GENERATE_MMIC`, `GENERATE_MMIE`, RX flags like `DECRYPTED`, `PN_VALIDATED`, `MIC_STRIPPED`, and `ALLOW_SAME_PN`, and station/link address handling for management frames.

## Risks And Edge Cases
Replay protection is sensitive to byte order and per-queue/security-index selection. Incorrect hardware flags can double-insert or omit IV/MIC/MMIE fields. CCMP/GCMP management frames with unicast addresses can use `rx->link_addrs` for AAD/nonce computation, so MLO/link-address plumbing must be correct. TKIP MIC failure handling intentionally reports through cfg80211 and can trigger countermeasures. Many paths require linear skbs or sufficient headroom/tailroom and drop on allocation/format failures.

## Test Signals
Strong tests include known-answer TKIP/CCMP/GCMP/BIP vectors, PN replay and same-PN exception tests, hardware-offload flag matrix tests, MIC failure injection/reporting, short frame and malformed MMIE drops, management-frame AAD with link addresses, fragment PN storage, and skb headroom/tailroom failure tests.
