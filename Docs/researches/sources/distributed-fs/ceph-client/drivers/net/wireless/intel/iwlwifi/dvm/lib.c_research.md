# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/lib.c

## Purpose

`lib.c` contains DVM shared runtime helpers for firmware command safety, TX power, temperature, hardware-rate conversion, IBSS station management, TX FIFO flush, advanced Bluetooth coexistence, RX-chain selection, TX antenna cycling, and WoWLAN programming. It is a support layer used by mac80211 callbacks, main lifecycle code, scan/rate/station code, and power/thermal handlers.

## Important APIs, Types, and Functions

Exports include `iwlagn_hw_valid_rtc_data_addr()`, `iwlagn_send_tx_power()`, `iwlagn_temperature()`, `iwlagn_hwrate_to_mac80211_idx()`, `iwlagn_manage_ibss_station()`, `iwlagn_txfifo_flush()`, `iwlagn_dev_txfifo_flush()`, `iwlagn_send_advance_bt_config()`, `iwlagn_bt_adjust_rssi_monitor()`, `iwlagn_bt_coex_rssi_monitor()`, `iwlagn_bt_rx_handler_setup()`, `iwlagn_bt_setup_deferred_work()`, `iwlagn_bt_cancel_deferred_work()`, `iwlagn_set_rxon_chain()`, `iwl_toggle_tx_ant()`, `iwlagn_send_patterns()`, `iwlagn_suspend()`, `iwl_dvm_send_cmd()`, and `iwl_dvm_send_cmd_pdu()`.

Key local helpers cover BT traffic/SCO classification, BT notification parsing, kill-mask and reduced-TX-power decisions, RX-chain count calculation, TKIP P1K conversion, and WoWLAN key iteration.

## Control Flow

Command paths should use `iwl_dvm_send_cmd()` or `_pdu()`, which reject RF-kill/CT-kill, firmware-error, and unloaded-firmware states; synchronous commands assert `priv->mutex`. TX power checks scanning state, clamps requested half-dBm power to NVM regulatory max, selects command version by firmware API, and sends the power command. TX FIFO flush builds v2/v3 command payloads depending on firmware API and queue masks, optionally stops/wakes mac80211 queues around device-wide flush.

BT coexistence starts with initial config in `main.c`, then runtime notifications are dispatched to `iwlagn_bt_coex_profile_notif()`. That updates traffic load/status/SCO state, queues work for chain/SMPS/RSSI monitor changes, and queues runtime config if reduced TX power or ACK/CTS kill masks changed. `iwlagn_set_rxon_chain()` then computes active/idle RX chains from valid antennas, chain-noise calibration, SMPS, power state, and BT traffic.

WoWLAN suspend flow cancels scans, restarts hardware with WoWLAN firmware, commits saved RXON, sets power mode, reprograms keys and replay counters, sends D3 config, wake filters, and packet patterns.

## State and Persistence Behavior

This file updates `priv->temperature`, `tx_power_user_lmt`-derived firmware state, IBSS station IDs, BT flags/masks/traffic load/RSSI monitor context/reduced-power state, `current_ht_config.smps`, RXON staging `rx_chain`, WoWLAN flags/key material command payloads, firmware loaded state during suspend, and command gating around `priv->status`. It also touches mac80211 queues and RSSI reporting state.

## Dependencies and Integration Points

Dependencies include mac80211 station/key/WoWLAN APIs, iwl transport command send/free operations, firmware command IDs and structures, module parameters, station/key helpers, scan cancellation, RXON commit, power update, thermal handler, rate tables, and BT/coex constants.

## Risks and Edge Cases

BT coexistence has many asynchronous updates and relies on ordered work plus `priv->mutex`; stale notifications during scans are deferred. `iwlagn_fill_txpower_mode()` only examines the BSS context, which can be wrong for multi-context scenarios. `iwl_toggle_tx_ant()` returns antenna index 0 under high 2.4 GHz BT load regardless of valid mask assumptions. WoWLAN key programming temporarily drops `priv->mutex` for mac80211 key iteration; this is considered acceptable in suspend but remains a lock-ordering-sensitive path. Command wrappers return `-EIO` for many states, so callers must handle reset/rfkill cleanly.

## Test Signals

Exercise firmware command rejection under RF-kill/CT-kill/FW error/unloaded firmware, TX power clamp tests against enhanced EEPROM limits, FIFO flush with API v2/v3, BT profile notifications with SCO/A2DP/ACL/load transitions, RX-chain updates under SMPS and BT traffic, WoWLAN suspend with CCMP/TKIP/WEP and patterns, and lockdep around suspend key iteration.
