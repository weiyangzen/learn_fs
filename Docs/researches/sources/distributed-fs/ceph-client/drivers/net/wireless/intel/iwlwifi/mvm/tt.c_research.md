# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/tt.c

## Purpose

`tt.c` implements MVM thermal throttling, critical-temperature kill, firmware temperature measurement, thermal-zone/cooling-device integration, and cTDP power-budget commands. It reacts to firmware temperature notifications or Linux thermal framework requests by changing radio operation: CT-kill state, dynamic SMPS, TX protection, TX backoff, and configurable thermal trip thresholds.

## Important APIs and functions

Temperature and CT-kill APIs include `iwl_mvm_temp_notif()`, `iwl_mvm_ct_kill_notif()`, `iwl_mvm_get_temp()`, `iwl_mvm_enter_ctkill()`, `iwl_mvm_tt_handler()`, and delayed work `check_exit_ctkill()`. Throttling actions are implemented by `iwl_mvm_tt_tx_backoff()`, `iwl_mvm_tt_tx_protection()`, and `iwl_mvm_tt_smps_iterator()`. cTDP and thermal framework integration uses `iwl_mvm_ctdp_command()`, `iwl_mvm_send_temp_report_ths_cmd()`, thermal-zone callbacks, cooling-device callbacks, `iwl_mvm_thermal_initialize()`, and `iwl_mvm_thermal_exit()`.

## Control flow

Firmware temperature notifications are parsed by `iwl_mvm_temp_notif_parse()`. If thermal throttling is host-managed, changed temperatures update `mvm->temperature` and call `iwl_mvm_tt_handler()`. If throttling is firmware-managed, threshold-crossing notifications update the Linux thermal zone when configured. CT-kill notifications enter hardware CT-kill state immediately.

`iwl_mvm_tt_handler()` compares the current temperature with configured thresholds. It enters/exits CT-kill, toggles dynamic SMPS on station interfaces, enables/disables TX protection per station, computes TX backoff from threshold table, and logs transition into or out of throttling. `check_exit_ctkill()` periodically restarts enough firmware state to read temperature for host-managed CT-kill and exits CT-kill once the exit threshold is reached.

`iwl_mvm_get_temp()` chooses between command-response temperature measurement and older notification-wait flow based on firmware command version. cTDP commands linearly map Linux cooling state to a firmware power budget between a minimum budget and a BIOS/default maximum. Thermal-zone registration exposes firmware-managed trips; cooling-device registration exposes cTDP states.

## State and persistence

State is stored in `mvm->thermal_throttle`: threshold parameters, throttle flag, dynamic SMPS flag, min/current TX backoff, CT-kill delayed work, and max power budget. Driver-wide state includes `mvm->temperature`, `mvm->temperature_test`, CT-kill status bit, thermal-zone trip array, cooling-device current state, and initialization status. Firmware commands persist TX backoff, cTDP budget, and temperature reporting thresholds until changed or reset.

## Dependencies and integration points

The file depends on firmware PHY operation commands and notifications, MVM firmware start/stop helpers, station TX protection, SMPS updates, BIOS power limit retrieval, Linux thermal framework under `CONFIG_THERMAL`, delayed work, and notification waits. It integrates with runtime firmware state and must avoid temperature polling when firmware is not regular/running.

## Risks

Thermal code is high impact because mistakes can leave hardware transmitting while overheated or stuck in CT-kill. Threshold hysteresis must be correct to avoid oscillation. Host-managed CT-kill temporarily starts/stops firmware to read temperature, so failures reschedule rather than clearing CT-kill. cTDP budget calculation must respect BIOS/default bounds. Thermal framework callbacks must reject invalid states and avoid firmware commands when firmware is unavailable. Test mode suppresses automatic temperature updates and CT-kill exit scheduling, which can surprise generic thermal tests.

## Test signals

Validation should cover notification parsing, negative temperature clamping, command-response and notification-based temperature measurement, CT-kill entry/exit/reschedule behavior, dynamic SMPS and TX protection threshold hysteresis, TX backoff table selection, firmware-managed thermal trip updates, cTDP state-to-budget mapping, BIOS power-limit bounds, thermal-zone trip sorting, cooling-device callbacks, and initialization/exit cleanup.
