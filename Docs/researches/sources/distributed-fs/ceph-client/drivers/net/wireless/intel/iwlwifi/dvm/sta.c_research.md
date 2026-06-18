# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/sta.c

## Purpose
`sta.c` manages DVM firmware station table state. It adds, modifies, removes, deactivates, clears, and restores firmware stations; builds default link-quality commands for local/broadcast stations; manages static WEP and dynamic per-station keys; allocates and updates broadcast stations; and issues station modifications for TX enable, RX aggregation, and sleep TX count.

This file is the central consistency layer between mac80211 station objects, driver station bookkeeping, and firmware `REPLY_ADD_STA`/`REPLY_REMOVE_STA`/`REPLY_TX_LINK_QUALITY_CMD` commands.

## Important APIs, Types, And Functions
- `iwl_send_add_sta()` sends `REPLY_ADD_STA`, optionally synchronously with response validation.
- `iwl_add_sta_callback()` and `iwl_process_add_sta_resp()` handle asynchronous add-station responses.
- `iwl_prep_station()` assigns or reuses a station id, initializes `priv->stations[sta_id].sta`, sets context id, and applies HT flags.
- `iwl_add_station_common()` prepares and synchronously adds a station to firmware.
- `iwl_remove_station()` removes a driver-active/ucode-active station and sends `REPLY_REMOVE_STA`.
- `iwl_deactivate_station()` clears driver-active state without sending removal, used when firmware is not necessarily updated immediately.
- `iwl_clear_ucode_stations()` clears software ucode-active bits after firmware operations, such as unassociated RXON, implicitly clear the firmware table.
- `iwl_restore_stations()` re-adds driver-active stations missing from firmware and resends saved LQ commands.
- `iwl_sta_fill_lq()`, `iwl_sta_alloc_lq()`, and `iwl_send_lq_cmd()` build and send default link-quality commands.
- `iwl_is_ht40_tx_allowed()`, `iwl_sta_calc_ht_flags()`, and `iwl_sta_update_ht()` compute and update per-station HT flags.
- Static WEP functions are `iwl_set_default_wep_key()`, `iwl_remove_default_wep_key()`, and `iwl_restore_default_wep_keys()`.
- Dynamic key functions are `iwl_set_dynamic_key()`, `iwl_remove_dynamic_key()`, `iwl_update_tkip_key()`, and helper `iwlagn_send_sta_key()`.
- Broadcast/local station helpers are `iwlagn_add_bssid_station()`, `iwlagn_alloc_bcast_station()`, `iwl_update_bcast_station()`, `iwl_update_bcast_stations()`, and `iwl_dealloc_bcast_stations()`.
- Aggregation/station modify helpers are `iwl_sta_tx_modify_enable_tid()`, `iwl_sta_rx_agg_start()`, `iwl_sta_rx_agg_stop()`, and `iwl_sta_modify_sleep_tx_count()`.

## Control Flow
Adding a station begins with `iwl_add_station_common()`. Under `sta_lock`, it calls `iwl_prep_station()` to choose a fixed AP/broadcast id or a free peer id, reject in-progress duplicates, initialize command fields, increment `num_stations`, store context id, attach the context to mac80211 station private data, and set HT flags. It marks `IWL_STA_UCODE_INPROGRESS`, copies the command, unlocks, and sends it synchronously. On successful firmware response, `iwl_send_add_sta()` activates the ucode bit; on failure, the driver-active and in-progress bits are cleared.

Removal checks readiness and station state under `sta_lock`, clears local LQ storage if needed, clears TID aggregation data, clears `IWL_STA_DRIVER_ACTIVE`, decrements station count, then sends `REPLY_REMOVE_STA`. Firmware success calls `iwl_sta_ucode_deactivate()` unless removal is temporary, which clears ucode-active and zeros the station entry.

RXON transitions can clear firmware station state without explicit remove commands. `iwl_clear_ucode_stations()` clears only software ucode-active bits, and `iwl_restore_stations()` later finds driver-active but not ucode-active entries, marks them in progress, sends add-station commands, and optionally resends their cached LQ commands. During WoWLAN restore it creates a simple default LQ instead of trusting the saved command.

Key programming is station modification. Static WEP uses a context-level WEP command with four slots. Dynamic CCMP/TKIP/WEP keys allocate a firmware key-cache offset, build station key flags, copy key material, and send an add-station modify with `STA_MODIFY_KEY_MASK`. TKIP updates can be asynchronous after scan cancellation.

Aggregation and TID modifications copy the current station command under lock, set the relevant modify mask and TID fields, unlock, and send `REPLY_ADD_STA` modify commands.

## State And Persistence Behavior
Persistent software state lives in `priv->stations[]`, `priv->num_stations`, `priv->tid_data[][]`, `priv->ucode_key_table`, and per-context WEP/key counters. Each station has `used` flags such as `IWL_STA_DRIVER_ACTIVE`, `IWL_STA_UCODE_ACTIVE`, `IWL_STA_UCODE_INPROGRESS`, `IWL_STA_LOCAL`, and `IWL_STA_BCAST`.

Firmware-visible state includes the firmware station table, per-station HT flags, key mappings, BA/TID settings, sleep TX count, and link-quality command. Firmware can implicitly clear station/key state during RXON transitions, so this file separates driver-active and ucode-active state to support restoration.

LQ commands for local/broadcast stations are heap allocated and stored in `priv->stations[sta_id].lq`; normal peer LQ commands are owned by rate-control station private state and referenced from the station table.

## Dependencies And Integration Points
The file depends on DVM command sending, firmware station/key command layouts, `sta_lock`, `priv->mutex` for operations that sleep or coordinate with RXON, mac80211 station/HT/key APIs, rate definitions from `rs.h`, RXON context state, and aggregation TID state. It is called from mac80211 station/key callbacks elsewhere in the driver, from RXON commit/restore logic in `rxon.c`, from rate scaling in `rs.c`, and from RX dispatch for add-station responses.

`iwl_send_lq_cmd()` is a major integration point for `rs.c`; it validates station active state and rejects HT LQ tables when the current RXON context is not HT-enabled.

## Risks And Edge Cases
- Station state is split between driver-active, ucode-active, and in-progress bits. Missing a bit transition can leak station slots, duplicate adds, or skip restoration.
- `iwl_prep_station()` increments `num_stations` when preparing a new station; all failure paths must decrement or clear state correctly.
- Add-station in-progress serialization protects firmware from concurrent add requests. New asynchronous paths must respect it.
- `iwl_send_lq_cmd()` rejects HT rates on non-HT channels to avoid a known disconnect race; callers must handle `-EINVAL`.
- Key-cache offsets are global bits. Failure to clear bits on key install/remove errors can exhaust hardware key slots.
- Static WEP and dynamic key paths differ. RXON unassociated transitions clear firmware WEP keys and require explicit restore.
- TKIP update cancels scan but, if cancellation fails, leaves a brief reliance on software decryption.
- Broadcast station LQ update replaces heap memory under `sta_lock`; concurrent users must follow existing lock/lifetime assumptions.
- Remove/deactivate behavior intentionally returns success when device is not ready, because teardown often removes stations after firmware shutdown.

## Test Signals
Test station add/remove/readd, AP station and broadcast station IDs, duplicate add handling, firmware add failure statuses, RXON station clear plus restore, WoWLAN station restore, HT flag updates for SMPS/HT40/AMPDU factor/density, LQ validation on HT and non-HT channels, default WEP set/remove/restore, dynamic CCMP/TKIP/WEP keys, key slot exhaustion and cleanup, TKIP phase1 updates during scans, RX aggregation start/stop, TID TX enable, sleep TX count modify, and teardown while device is not ready.
