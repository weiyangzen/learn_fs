# sources/distributed-fs/ceph-client/net/mac80211/tkip.c

## Purpose
This file implements TKIP key mixing, IV construction, payload encryption, and payload decryption for mac80211 software crypto and hardware-assist paths. It bridges 802.11 TKIP packet fields, per-key TKIP phase state, WEP/RC4 payload encryption helpers, replay detection, and optional driver upload of phase-1 keys.

## Important APIs, types, and functions
- `tkip_sbox[]` and `tkipS()` implement the TKIP S-box operation used in key mixing.
- `write_tkip_iv()` writes the three byte TKIP IV prefix from IV16.
- `tkip_mixing_phase1()` computes P1K from temporal key, transmitter address, and IV32, then records `TKIP_STATE_PHASE1_DONE` and `p1k_iv32` in `struct tkip_ctx`.
- `tkip_mixing_phase2()` derives the 16-byte per-packet RC4 key from cached P1K and IV16.
- `ieee80211_tkip_add_iv()` is exported GPL and writes TKIP IV/Ext IV/key index fields for a packet number.
- `ieee80211_get_tkip_p1k_iv()`, `ieee80211_get_tkip_rx_p1k()`, and `ieee80211_get_tkip_p2k()` are exported helper APIs used by drivers or hardware crypto paths to obtain phase keys.
- `ieee80211_tkip_encrypt_data()` derives the per-packet key and calls `ieee80211_wep_encrypt_data()`.
- `ieee80211_tkip_decrypt_data()` validates IV/key index/replay, optionally updates hardware phase-1 state through `drv_update_tkip_key()`, decrypts through `ieee80211_wep_decrypt_data()`, and returns TKIP-specific status codes.

## Control flow
TX starts when `wpa.c` pushes IV space, increments `key->conf.tx_pn`, calls `ieee80211_tkip_add_iv()`, and, for software crypto, calls `ieee80211_tkip_encrypt_data()`. Encryption reads the packet IV from the skb, computes or reuses P1K under `key->u.tkip.txlock`, runs phase 2, and encrypts the payload/ICV area with RC4 through WEP helpers.

RX starts when `wpa.c` calls `ieee80211_tkip_decrypt_data()` with the 802.11 payload. The function checks minimum length, parses IV16/keyid/IV32, requires Ext IV, verifies the key index, and rejects replays against the selected receive queue context. In hardware-decrypted `only_iv` mode it marks the receive context as hardware-uploaded and skips RC4. Otherwise it computes phase 1 if state is uninitialized or IV32 changed, optionally calls the driver's `update_tkip_key` callback when hardware needs P1K, computes phase 2, decrypts bytes after the 8-byte TKIP IV, and on success reports IV32/IV16 back to the caller for later replay-counter commit after MIC verification.

## State and persistence
Transmit state lives in `key->u.tkip.tx`: cached P1K, `p1k_iv32`, state enum, and `txlock`. Receive state is per queue in `key->u.tkip.rx[queue]`, tracking IV32/IV16 and a phase context. This state persists for the lifetime of the key and is not stored outside kernel memory. The code deliberately does not advance RX replay state directly on decrypt success; it returns the observed IV so the caller can commit it only after Michael MIC verification.

## Dependencies and integration points
The implementation depends on `key.h` for internal key layout, `driver-ops.h` for hardware key updates, `wep.h` for RC4 encryption/decryption, unaligned little-endian access helpers, and public `<net/mac80211.h>` definitions. `wpa.c` is the main software path caller. Driver-visible helpers are exported for devices that need TKIP phase keys. Hardware integration occurs when `KEY_FLAG_UPLOADED_TO_HARDWARE` and `local->ops->update_tkip_key` are set.

## Risks and edge cases
TKIP is legacy crypto; correctness is mostly about compatibility and safe replay handling rather than modern security. Queue index validity is assumed by the caller. The RX replay exception allows the first TSC 0 frame only when the context is completely uninitialized, matching 802.11 compatibility rules but requiring careful state management. P1K caching can recompute often for out-of-order access categories, and locking must remain correct because TX phase state is shared. The `ra` parameter in decrypt is currently unused, so changes expecting receiver-address-specific behavior need scrutiny.

## Test signals
No direct KUnit tests are in this item. Useful signals are mac80211 crypto RX/TX tests, interoperability with TKIP APs, hardware crypto tests that exercise `update_tkip_key`, replay rejection tests, and static checks for exported symbol users. Tracepoint `drv_update_tkip_key` can confirm hardware phase-1 upload behavior.
