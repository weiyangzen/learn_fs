# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/ipw2x00/libipw_crypto_wep.c

## Purpose
Implements host-based WEP encryption and decryption for libipw as the `WEP` crypto plugin. It handles RC4 key construction from IV plus shared key, IV insertion, ICV generation/verification, simple weak-IV avoidance, key set/get, and stats printing.

## Important APIs, Types, and Functions
`struct libipw_wep_data` stores the transmit IV counter, WEP key bytes and length, key index, and TX/RX ARC4 contexts. Important functions are `libipw_wep_init`, `libipw_wep_deinit`, `libipw_wep_build_iv`, `libipw_wep_encrypt`, `libipw_wep_decrypt`, `libipw_wep_set_key`, `libipw_wep_get_key`, `libipw_wep_print_stats`, `libipw_crypto_wep_init`, and `libipw_crypto_wep_exit`.

## Control Flow
Initialization rejects WEP in FIPS mode, allocates per-key state, records the key index, and randomizes the starting IV. TX requires four bytes of headroom and tailroom, pushes the 4-byte WEP IV/key-index field between header and payload, skips known weak RC4 IV patterns, appends little-endian CRC32 ICV over plaintext payload, and ARC4-encrypts payload plus ICV. RX reads the IV and key index, validates it matches the context key index, derives the ARC4 key, decrypts payload plus ICV, verifies CRC32, then removes IV and ICV from the SKB.

## State and Persistence Behavior
The WEP context persists the IV counter and key bytes for a key slot. `set_key()` accepts lengths up to 13 bytes, copies key material, and updates `key_len`. `get_key()` returns the stored key if the caller buffer is large enough. `deinit()` uses `kfree_sensitive()` to clear key material. There is no replay protection beyond WEP's weak IV mechanics.

## Dependencies and Integration Points
Depends on libipw's crypto registry, kernel ARC4, CRC32, random bytes, SKB head/tail operations, and FIPS status. `libipw_wx_set_encode()` creates WEP contexts for legacy key ioctls, while `libipw_wx_set_encodeext()` handles WEP through the extended API. `libipw_tx.c` and `libipw_rx.c` call this plugin through MPDU encrypt/decrypt hooks.

## Risks
WEP is cryptographically obsolete and disabled in FIPS mode. The code mutates SKBs in place and returns errors if headroom, tailroom, or length assumptions are violated. RX rejects frames whose key index does not match the context, so key-slot selection must match the IV byte. IV wrap and per-key IV reuse remain inherent WEP weaknesses. CRC failure returns a distinct negative value used by the RX debug path.

## Test Signals
Legacy WEP open/shared-key operation, 40-bit and 104-bit keys, default TX key switching, FIPS mode failure, bad ICV drops, wrong key index drops, SKB headroom/tailroom failure, key replacement under traffic, and module load/unload through Wireless Extensions are useful signals.
