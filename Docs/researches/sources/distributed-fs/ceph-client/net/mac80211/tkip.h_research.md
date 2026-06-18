# sources/distributed-fs/ceph-client/net/mac80211/tkip.h

## Purpose
This header declares the internal mac80211 TKIP software crypto entry points and decrypt result codes used by the WPA/TKIP receive and transmit paths.

## Important APIs, types, and functions
- `ieee80211_tkip_encrypt_data()` encrypts a TKIP payload using an ARC4 context, internal key, skb-derived IV fields, and payload pointer/length.
- `TKIP_DECRYPT_OK`, `TKIP_DECRYPT_NO_EXT_IV`, `TKIP_DECRYPT_INVALID_KEYIDX`, and `TKIP_DECRYPT_REPLAY` define status codes returned by the decrypt helper.
- `ieee80211_tkip_decrypt_data()` validates and decrypts a TKIP payload and reports IV32/IV16 to the caller on success.

## Control flow
The header is included by TKIP implementation and WPA crypto code. Callers pass an already selected `struct ieee80211_key`, packet buffer information, transmitter/receiver address context, hardware-decrypt mode, security queue index, and output IV pointers. The return code determines whether the RX path continues or drops the frame as a TKIP failure.

## State and persistence
The header declares APIs that mutate per-key TKIP state in `struct ieee80211_key`, but it defines no storage itself. Output IV parameters are transient handoff state used by the caller before committing replay counters after MIC validation.

## Dependencies and integration points
It includes kernel type definitions, crypto declarations for `struct arc4_ctx`, and `key.h` for the internal mac80211 key type. This is not a public driver API header; driver-facing phase-key helpers are exported from `tkip.c` through other declarations in public/internal headers.

## Risks and edge cases
The decrypt status enum uses negative values that overlap ordinary error-style returns, while success is zero. Callers must not collapse all negative values if they need diagnostics. Since function parameters include raw payload pointers and lengths, callers must ensure skb linearization and minimum length checks match the implementation's expectations.

## Test signals
Compilation of `wpa.c` and `tkip.c` verifies declaration compatibility. Runtime signals come from TKIP encrypted TX/RX, replay rejection, and hardware-decrypted `only_iv` paths.
