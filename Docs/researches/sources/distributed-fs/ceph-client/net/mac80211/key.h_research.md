# sources/distributed-fs/ceph-client/net/mac80211/key.h

## Purpose
`key.h` defines mac80211 internal key data structures, constants, state enums, and prototypes used by key installation, software crypto, hardware offload, station management, link management, and debugfs. It is the internal contract for `key.c` and all users that need to store, dereference, switch, free, or report keys.

## Important APIs, Types, And Functions
The header defines `NUM_DEFAULT_KEYS`, `NUM_DEFAULT_MGMT_KEYS`, `NUM_DEFAULT_BEACON_KEYS`, and `INVALID_PTK_KEYIDX`. `enum ieee80211_internal_key_flags` carries `KEY_FLAG_UPLOADED_TO_HARDWARE` and `KEY_FLAG_TAINTED`. `enum ieee80211_internal_tkip_state`, `struct tkip_ctx`, and `struct tkip_ctx_rx` describe TKIP phase/key-cache state. `struct ieee80211_key` embeds owner pointers, list membership, flags, cipher-specific state unions for TKIP, CCMP, AES-CMAC, AES-GMAC, GCMP, and generic PN tracking, optional debugfs pointers, a key color, and trailing `struct ieee80211_key_conf` with variable-length key material.

## Control Flow
The header itself has no executable control flow, but its layout drives all key paths. Callers allocate a key with `ieee80211_key_alloc()`, attach it with `ieee80211_key_link()`, mark PTK TX use with `ieee80211_set_tx_key()`, update defaults through the default-key helpers, remove per-link or per-interface keys through the free helpers, and re-enable or switch hardware offload through `ieee80211_reenable_keys()` and `ieee80211_key_switch_links()`. The delayed tailroom work callback is declared here for interface initialization in `iface.c`.

## State And Persistence
The central persistent object is `struct ieee80211_key`, which lives until the key is unlinked and RCU/network readers have drained. Cipher unions preserve replay counters, packet numbers, TKIP phase state, and precomputed crypto transforms. The key color is used to distinguish fragments or cached state across replacements. Because `ieee80211_key_conf` is last and contains key material, allocation size and free paths must treat it as sensitive variable-length storage.

## Dependencies And Integration Points
The header includes Linux list/crypto/RCU types, ARC4 and AES-CBC-MAC crypto headers, and public `<net/mac80211.h>`. It forward-declares `ieee80211_local`, `ieee80211_sub_if_data`, `ieee80211_link_data`, and `sta_info`, keeping the full definitions in `ieee80211_i.h` and station headers. It is included by key management, MLO link teardown, interface teardown, station cleanup, and crypto/debugfs code.

## Risks And Edge Cases
`struct ieee80211_key` mixes RCU-visible pointers, wiphy-mutex-protected flags, spinlock-protected TKIP TX state, and sensitive key material. Any layout change can affect variable-length allocation, debugfs expectations, or software crypto. The key index constants define the valid split among data, management, and beacon keys; off-by-one errors here can corrupt default-key selection. `INVALID_PTK_KEYIDX` intentionally points to a NULL PTK slot and must remain outside the valid active PTK key IDs used for Extended Key ID.

## Test Signals
Header-level validation is mostly compile-time: all users must agree on struct layout, constants, and prototypes. Runtime signals come from key allocation/free tests for every cipher, Extended Key ID PTK tests, per-link GTK tests, debugfs key visibility, RCU/key iteration tests, and memory-sanitizer checks that sensitive key storage is released through the intended free path.
