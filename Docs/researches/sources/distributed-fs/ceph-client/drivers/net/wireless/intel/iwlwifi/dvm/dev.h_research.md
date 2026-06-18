# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/dev.h

## Purpose

`dev.h` is the private state and implementation-contract header for the legacy Intel iwlwifi DVM op-mode. It defines the constants, calibration state, aggregation state, RXON context model, device-family configuration hooks, Bluetooth coexistence parameters, per-station/per-vif private data, power/thermal/debug state, and the central `struct iwl_priv` used by the DVM source files. It deliberately separates driver-internal definitions from firmware command ABI definitions in `commands.h`.

## Important APIs, Types, and Functions

Important declarations include CT-kill thresholds, RTS/MSDU/MPDU defaults, scan-rate constants, sensitivity/chain-noise calibration constants, `union iwl_ht_rate_supp`, `struct iwl_ht_config`, `struct iwl_qos_info`, `enum iwl_agg_state`, `struct iwl_ht_agg`, `struct iwl_tid_data`, `struct iwl_station_entry`, `struct iwl_station_priv`, `struct iwl_vif_priv`, `struct iwl_sensitivity_ranges`, `struct iwl_sensitivity_data`, `struct iwl_chain_noise_data`, `struct iwl_event_log`, `struct iwl_rf_reset`, `enum iwl_rxon_context_id`, `struct iwl_rxon_context`, `struct iwl_hw_params`, `struct iwl_dvm_bt_params`, `struct iwl_dvm_cfg`, `struct iwl_wipan_noa_data`, and the large `struct iwl_priv`.

The header also exposes conversion/access helpers: `IWL_OP_MODE_GET_DVM()`, `IWL_MAC80211_GET_DVM()`, `iwl_rxon_ctx_from_vif()`, `for_each_context()`, `iwl_is_associated_ctx()`, `iwl_is_associated()`, and `iwl_is_any_associated()`. `iwl_update_chain_flags()` and `iwl_bcast_addr` are forward declarations used across device-family code.

## Control Flow

The structures in this file define how the rest of the DVM driver sequences work. `struct iwl_priv` is allocated inside the mac80211 `hw->priv` area and then threaded through op-mode, mac80211, transport, firmware command, scan, station, power, BT coexistence, thermal throttling, WoWLAN, LED, debugfs, and recovery paths. RXON contexts represent BSS and PAN firmware contexts; `for_each_context()` lets lifecycle paths update every valid context without hard-coding PAN support.

Aggregation flow is modeled per station/TID through `struct iwl_tid_data` and `struct iwl_ht_agg`: start/operational/emptying/stop states coordinate TX reply, compressed BA, queue ID, sequence number, and mac80211 notification readiness. Calibration flow stores sensitivity and chain-noise accumulators in `iwl_priv`, while device-family callbacks in `struct iwl_dvm_cfg` provide runtime hooks for hardware parameter setup, channel switch command shape, NIC config, and temperature conversion.

## State and Persistence Behavior

`struct iwl_priv` contains nearly all persistent software state for a DVM device: status bits, mutex/spinlock-protected station tables, queue stop counters, queue-to-mac80211 mappings, active and staging RXON commands, scan request state, current temperature, firmware reload counters, statistics snapshots, BT coexistence state, calibration state, rate-control state, power manager, thermal throttle state, WEP/key state, WoWLAN key material, LED registration state, NVM/EEPROM data, delayed work/timers, and current firmware image type.

The state is not inherently synchronized by this header. Callers must follow the comments: station table access generally requires `sta_lock`, most firmware command/lifecycle changes require `priv->mutex`, and RCU protects `noa_data`.

## Dependencies and Integration Points

`dev.h` depends on Linux interrupt/wait/LED/slab/mutex APIs, mac80211-facing types through included iwlwifi headers, firmware image definitions, NVM utilities, CSR/register definitions, debugging, transport, notification waits, and local DVM headers `led.h`, `power.h`, `rs.h`, and `tt.h`. It is consumed by nearly every DVM translation unit.

## Risks and Edge Cases

The main risk is contract drift: many fields are updated by separate files with implicit locking and status-bit assumptions. RXON context `active` is `const` to force explicit casts at hardware-update sites, so accidental direct mutation is discouraged but still possible. Aggregation, station, and queue state can become inconsistent if firmware error/restart paths do not clear all tables in sync with mac80211 reconfiguration. The many feature-dependent fields under `CONFIG_IWLWIFI_DEBUGFS`, `CONFIG_IWLWIFI_LEDS`, and `CONFIG_PM_SLEEP` require compile coverage across configs.

## Test Signals

Useful signals are allmodconfig/build coverage, lockdep during start/stop/reset/scan/AMPDU paths, mac80211 station and vif lifecycle tests, suspend/resume with WoWLAN enabled and disabled, BT coexistence notification handling, and firmware restart recovery checks that verify station/key/aggregation/queue state is reset consistently.
