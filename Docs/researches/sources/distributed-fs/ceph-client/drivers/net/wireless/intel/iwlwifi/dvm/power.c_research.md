# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/dvm/power.c

## Purpose

`power.c` builds and sends DVM firmware power-table commands. It maps mac80211 power-save/idle/DTIM state, module parameters, WoWLAN, thermal throttling, advanced power-management support, BT coexistence, shadow-register support, and PCI bus power management into `struct iwl_powertable_cmd` values.

## Important APIs, Types, and Functions

Exported functions are `iwl_power_set_mode()`, `iwl_power_update_mode()`, and `iwl_power_initialize()`. Local helpers include `iwl_static_sleep_cmd()`, `iwl_power_sleep_cam_cmd()`, `iwl_set_power()`, and `iwl_power_build_cmd()`. The file defines `force_cam` module parameter, legacy and advanced power vector tables for DTIM ranges 0-2, 3-10, and greater than 10, plus `struct iwl_power_vec_entry`.

## Control Flow

`iwl_power_update_mode()` builds a command and delegates to `iwl_power_set_mode()`. Command construction first honors `force_cam`, then chooses DTIM period, WoWLAN maximum sleep level, idle maximum sleep when supported, thermal-throttle power mode, CAM when mac80211 PS is disabled, debug override, module `power_level`, or default level 1. `iwl_static_sleep_cmd()` selects legacy or advanced tables based on `priv->lib->adv_pm`, chooses DTIM range, adjusts sleep intervals for skip-DTIM/listen interval constraints, sets sleep-over-DTIM, shadow register, BT SCO, PCI PM flags, clamps to `IWL_CONN_MAX_LISTEN_INTERVAL`, and enforces monotonic/max interval limits.

`iwl_power_set_mode()` requires `priv->mutex`, skips unchanged commands unless forced, rejects RF-not-ready, caches `sleep_cmd_next`, defers non-forced updates while scanning, enables PMI before allowing sleep, sends `POWER_TABLE_CMD`, disables PMI for CAM on success, updates RX chain flags when chain-noise calibration permits, and commits `sleep_cmd`.

## State and Persistence Behavior

Persistent state includes `priv->power_data.sleep_cmd`, `sleep_cmd_next`, `debug_sleep_level_override`, and `bus_pm`. The file toggles `STATUS_POWER_PMI` indirectly through `iwl_dvm_set_pmi()`, may update RXON chain state through `iwl_update_chain_flags()`, and programs firmware power-table state. It reads mac80211 config flags, DTIM period, WoWLAN state, thermal state, BT params, transport PM support, and module parameters.

## Dependencies and Integration Points

Dependencies include mac80211 config, DVM command wrappers, transport PM capability, thermal throttle helpers, BT coexistence helpers, RX-chain update logic, firmware power command definitions, and module parameters. `main.c` initializes power state and calls power update after firmware alive; `lib.c` calls it during WoWLAN setup.

## Risks and Edge Cases

`force_cam` defaults true, so normal runtime power saving is disabled unless the module parameter changes. Scan deferral means `sleep_cmd_next` can differ from firmware state until scan completion. Chain updates are skipped during chain-noise calibration. DTIM zero is normalized specially. Advanced and legacy table layouts differ; incorrect `adv_pm` config can send incompatible flags. All synchronous paths require `priv->mutex`.

## Test Signals

Exercise CAM default, explicit power levels 1-5, debug override, WoWLAN mode, idle mode, thermal throttling modes, DTIM 0/1/2/3/10/11, scan deferral and later apply, PCI PM flag, shadow register flag, BT SCO flag, RF-not-ready rejection, and RX chain update behavior around calibration states.
