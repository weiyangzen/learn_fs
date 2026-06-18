# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/thermal.c

Purpose: Implements MLD thermal handling: CT-kill notification and delayed recovery, firmware temperature threshold configuration, Linux thermal zone registration, cTDP cooling-device control, and platform power-budget selection.

Important APIs and functions: `iwl_mld_handle_ct_kill_notif()` enters CT-kill and schedules exit. `iwl_mld_handle_temp_notif()` handles DTS threshold notifications. `iwl_mld_config_temp_report_ths()` sends firmware trip thresholds. Under `CONFIG_THERMAL`, thermal zone ops read temperature and update trips, cooling ops map cooling state to cTDP budget through `iwl_mld_config_ctdp()`. `iwl_mld_thermal_initialize()` and `iwl_mld_thermal_exit()` manage lifecycle.

Control flow: Initialization sets up delayed CT-kill exit work, computes max power budget from RF type and BIOS power limit, and optionally registers thermal cooling and zone devices. CT-kill notifications set ctkill true and schedule a delayed work to clear it. Thermal-zone trip changes compress/sort configured trip temperatures and send them to firmware. Cooling state changes scale linearly from max power budget down to a minimum cTDP budget and send `CTDP_CONFIG_CMD`.

State and persistence: Mutates `mld->power_budget_mw`, `mld->cooling_dev.cur_state/cdev`, `mld->tzone`, and ctkill state. Runtime only; BIOS/ACPI power limit is read during initialization but not persisted by this code.

Dependencies and integration points: Depends on firmware PHY thermal APIs, iwl BIOS power-limit helper, Linux thermal framework, wiphy delayed work and locking, transport RF ID macros, and MLD ctkill state setter.

Risks: Temperature unit conversions cross Celsius, millicelsius, signed 16-bit firmware thresholds, and firmware response values. Thermal callbacks must handle firmware not running. Budget scaling assumes `power_budget_mw >= IWL_MLD_MIN_CTDP_BUDGET_MW`. Registration failure paths set pointers to NULL but thermal-zone enable failure unregisters without explicitly clearing in the shown path.

Test signals: Cover CT-kill enter/exit scheduling, negative temperature rejection, threshold index bounds, trip compression/sort, get-temp response length failure, cTDP state range and budget math, BIOS limit selection, and init/exit with and without `CONFIG_THERMAL`.
