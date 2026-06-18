# sources/distributed-fs/ceph-client/drivers/net/wireless/ralink/rt2x00/rt2x00crypto.c

## Purpose
Provides common hardware-crypto helper routines for rt2x00. It maps mac80211 cipher IDs into rt2x00 cipher enums, annotates TX descriptors for hardware encryption, computes crypto overhead, saves/removes/reinserts TX IV data, and reconstructs stripped RX IV/ICV material when hardware provides it separately.

## Important APIs, Types, And Functions
Exports `rt2x00crypto_key_to_cipher()`, `rt2x00crypto_create_tx_descriptor()`, `rt2x00crypto_tx_overhead()`, `rt2x00crypto_tx_copy_iv()`, `rt2x00crypto_tx_remove_iv()`, `rt2x00crypto_tx_insert_iv()`, and `rt2x00crypto_rx_insert_iv()`. It uses `ieee80211_key_conf`, `skb_frame_desc`, `txentry_desc`, `rxdone_entry_desc`, and cipher enums.

## Control Flow
TX descriptor creation exits unless hardware crypto is enabled and mac80211 selected a hardware key. It sets encryption flags, pairwise flag, key index, IV offset/length, and whether hardware should generate IV/MMIC. TX overhead adds ICV and optionally IV/MMIC lengths when mac80211 does not generate them. TX remove/copy helpers preserve IV bytes in the skb descriptor, move the 802.11 header when stripping IV, and restore it before mac80211 TX status. RX insert chooses IV/ICV lengths by cipher, makes head/tail room while preserving or compensating L2 padding, copies IV and ICV from `rxdesc`, updates size, and clears `RX_FLAG_IV_STRIPPED`.

## State And Persistence
Crypto helpers mutate per-packet state only: `txentry_desc`, `skb_frame_desc->iv`, skb data pointers/lengths, and `rxdesc->size/flags`. They depend on persistent hardware crypto capability flags and key configuration installed through `rt2x00mac_set_key()`.

## Dependencies And Integration Points
Used by TX queue preparation and RX completion in rt2x00 core, and by debugfs crypto counters. Integrates with mac80211 key flags `GENERATE_IV`, `GENERATE_MMIC`, pairwise keys, and RT2800 key programming hooks.

## Risks
Header movement and skb push/pull operations are sensitive to headroom/tailroom assumptions established by queue code. IV length inference in `rt2x00crypto_tx_insert_iv()` derives from stored IV words and could fail for unexpected formats. RX AES ICV handling only fills 4 of 8 bytes because mac80211 strips it immediately. Unsupported ciphers map to `CIPHER_NONE`, forcing software paths.

## Test Signals
WEP40/WEP104/TKIP/CCMP TX and RX, pairwise and group keys, mac80211-generated versus hardware-generated IV/MMIC, MIC failure countermeasures, L2 padding plus crypto reconstruction, TX status skb restoration checks, and KASAN around skb manipulation.
