# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.c

`vega12_thermal.c` implements Vega12 thermal and fan-control callbacks used by the hwmgr vtable. It reads edge temperature, configures thermal interrupt thresholds, starts/stops alerts, reports fan RPM support, reads current RPM through SMU, programs fan target temperature, and starts/stops SMU-managed fan control.

Public functions are `vega12_thermal_get_temperature()`, `vega12_thermal_stop_thermal_controller()`, `vega12_fan_ctrl_get_fan_speed_info()`, `vega12_fan_ctrl_get_fan_speed_rpm()`, `vega12_fan_ctrl_reset_fan_speed_to_default()`, `vega12_fan_ctrl_stop_smc_fan_control()`, `vega12_thermal_disable_alert()`, `vega12_fan_ctrl_start_smc_fan_control()`, and `vega12_start_thermal_controller()`. Internal helpers set alert ranges, enable alert registers, and send `PPSMC_MSG_SetFanTemperatureTarget`.

Starting the controller validates the range, clamps thresholds against valid alert bounds and software shutdown temperature, programs `THM_THERMAL_INT_CTRL`, enables thermal interrupt clear bits, sends the fan target from the active SMU PPTable, and starts SMC fan control if the microcode fan-control platform cap is set. Stopping disables alerts. RPM reads send `PPSMC_MSG_GetCurrentRpm`.

The module modifies hardware registers and SMU runtime state but keeps little local state. It reads `hwmgr->pptable` and `hwmgr->backend`; fan feature enable/disable internals are compiled out, so start/stop currently do not toggle `GNLD_FAN_CONTROL` directly. Dependencies include Vega12 register definitions, SOC15 register access, SMU messages, PowerPlay thermal units, and platform caps.

Risks include register programming mistakes, threshold unit conversion errors, misleading auto/manual fan state due to compiled-out feature toggling, and relying on initialized PPTable/backend state. Test signals include thermal start/stop, suspend/resume, interrupt threshold behavior, fan RPM reads, fan target programming, and temperature consistency with SMU metrics.
