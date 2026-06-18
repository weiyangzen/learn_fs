# sources/distributed-fs/ceph-client/net/mac80211/debugfs_key.c

## Purpose

`debugfs_key.c` exposes per-key mac80211 debugfs diagnostics under the PHY `keys` directory. It reports key configuration, cipher suite, packet number state, replay/error counters, raw key bytes, interface association, and default-key symlinks.

## Important APIs, Types, And Functions

The exported functions are `ieee80211_debugfs_key_add()`, `ieee80211_debugfs_key_remove()`, `ieee80211_debugfs_key_update_default()`, `ieee80211_debugfs_key_remove_mgmt_default()`, and `ieee80211_debugfs_key_remove_beacon_default()`. Macro families `KEY_READ`, `KEY_CONF_READ`, `KEY_OPS`, and `KEY_CONF_OPS` generate many read-only files for `keylen`, `keyidx`, `hw_key_idx`, `flags`, and `ifindex`.

Cipher-specific handlers include `key_algorithm_read()`, `key_tx_spec_read()`/`key_tx_spec_write()`, `key_rx_spec_read()`, `key_replays_read()`, `key_icverrors_read()`, `key_mic_failures_read()`, and `key_key_read()`.

## Control Flow

`ieee80211_debugfs_key_add()` first checks that the PHY-level `keys` directory exists. It assigns a monotonically increasing static numeric directory name, records it in `key->debugfs.cnt`, creates the key directory, and, for station keys, creates a symlink back to the station debugfs directory. It then creates files for configuration fields, cipher algorithm, TX/RX PN state, replay/error counters, raw key material, and interface name.

`key_tx_spec_write()` rejects WEP, returns unsupported for TKIP, and accepts a 48-bit hex PN for CCMP/CMAC/BIP/GCMP families by atomically setting `key->conf.tx_pn`. Readers select different key union fields depending on cipher: TKIP IV32/IV16 arrays, CCMP/GCMP per-TID RX PN arrays including group slot, AES-CMAC/GMAC management PN, and replay/error counters. `ieee80211_debugfs_key_update_default()` recreates default unicast/multicast symlinks under an interface debugfs directory while holding the wiphy lock.

## State And Persistence

The debugfs tree mirrors runtime key objects. `key->debugfs.dir`, `stalink`, and `cnt` track dentries/symlink identity. Reads expose live key counters and packet numbers. Writes can mutate the key transmit PN for selected ciphers, which directly affects encryption/replay sequencing behavior. The static `keycount` only monotonically assigns debugfs names within the module lifetime and is not persisted.

## Dependencies And Integration Points

This file depends on `ieee80211_i.h`, `key.h`, `debugfs.h`, and `debugfs_key.h`. It consumes the PHY `local->debugfs.keys` directory created by `debugfs_hw_add()`. It links station keys to `debugfs_sta.c` station directories and interface default-key symlinks to netdev debugfs directories.

## Risks

The raw `key` file exposes key bytes through debugfs, so access controls and debugfs availability matter. TX PN writes are powerful test hooks and can create replay/security anomalies if used on a live link. `keycount` is static and not synchronized beyond normal mac80211/wiphy serialization expectations; unusual concurrent key creation should still be reviewed. Cipher switch statements must be updated for new cipher suites or they silently return empty data/default behavior.

## Test Signals

Coverage should create/remove keys for WEP, TKIP, CCMP, GCMP, AES-CMAC, and BIP-GMAC/CMAC, verify directories and station/default symlinks, read PN/replay/error files for each cipher, write boundary TX PN values including `2^48 - 1` and `2^48`, and confirm remove paths clear dentries without leaving stale default symlinks.
