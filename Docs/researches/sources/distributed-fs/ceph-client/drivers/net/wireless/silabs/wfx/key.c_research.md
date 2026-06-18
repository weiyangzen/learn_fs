# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/key.c

Purpose: Implements mac80211 key install/remove for WFx firmware key table entries.

Important APIs and functions: `wfx_set_key()` is the mac80211 callback. Internals allocate/free key table indexes with `wfx_alloc_key()`/`wfx_free_key()` and fill firmware key payloads for WEP pair/group, TKIP pair/group, CCMP pair/group, SMS4/WAPI pair/group, and AES-CMAC/IGTK group keys.

Control flow and integration: On `SET_KEY`, it allocates a firmware key index, reads initial RX sequence, fills `wfx_hif_req_add_key`, sends `wfx_hif_add_key()`, sets mac80211 flags for IV/tailroom handling, stores `hw_key_idx`, and returns success. On `DISABLE_KEY`, it frees the index and sends `wfx_hif_remove_key()`. The path is serialized by `wdev->conf_mutex`.

State and persistence: `wdev->key_map` tracks allocated firmware key slots. Firmware key entries persist until removed/reset. mac80211 `key->hw_key_idx` persists the slot mapping.

Dependencies: Depends on mac80211 key flags/sequences/cipher IDs, HIF key ABI, Ethernet helpers, and `memreverse()` for PN/IPN ordering.

Risks and test signals: Risks include key slot leaks on command failure, pairwise key without station, TKIP MIC key direction differences in AP vs STA, sequence counter endian/reversal, unsupported ciphers, and removing invalid indexes. Tests should cover all supported ciphers, group/pairwise paths, AP/STA TKIP group MIC selection, AES-CMAC MMIE generation, slot exhaustion, add-key failure rollback, and disable-key consistency.

Test signals: Source read size: 227 lines, 7619 bytes.
