# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega20_thermal.c

## Purpose
`vega20_thermal.c` implements Vega20 fan control and thermal alert helpers used by the hwmgr function table. It can switch between SMU microcode fan control and manual register-driven PWM/RPM modes, read hotspot temperature, program thermal interrupt thresholds, and send the fan target temperature to SMU.

## Important APIs, Types, and Functions
SMU fan-control feature toggles are `vega20_fan_ctrl_start_smc_fan_control()`, `vega20_fan_ctrl_stop_smc_fan_control()`, and their private enable/disable helpers. Manual fan access includes `vega20_fan_ctrl_get_fan_speed_pwm()`, `vega20_fan_ctrl_set_fan_speed_pwm()`, `vega20_fan_ctrl_get_fan_speed_rpm()`, `vega20_fan_ctrl_set_fan_speed_rpm()`, and `vega20_fan_ctrl_get_fan_speed_info()`. Temperature and alert handling includes `vega20_thermal_get_temperature()`, `vega20_thermal_disable_alert()`, `vega20_thermal_stop_thermal_controller()`, and `vega20_start_thermal_controller()`.

## Control Flow
Manual PWM/RPM setters first stop SMU fan control when microcode fan control is enabled, compute register units, write THM fan-control registers, and set static mode. Thermal startup validates a temperature range, programs high/low interrupt thresholds clamped by the PPTable software shutdown temperature, enables thermal interrupt clear bits, and sends `PPSMC_MSG_SetFanTemperatureTarget` using the uploaded SMU PPTable fan target.

## State and Persistence
The file mutates `data->smu_features[GNLD_FAN_CONTROL].enabled` when enabling or disabling firmware fan control. It reads the thermal controller and PPTable state from `hwmgr` and `hwmgr->pptable`. Manual fan settings are persisted only in hardware registers until changed, reset, or SMU control resumes.

## Dependencies and Integration Points
It depends on `vega20_hwmgr.h` for backend feature state, `vega20_smumgr.h` and `vega20_ppsmc.h` for SMU commands, `vega20_inc.h`/SOC15 macros for THM register access, and `pp_debug.h` for assertion/log macros. The hwmgr function table exposes these routines for generic thermal/fan operations.

## Risks
Fan control crosses firmware and direct-register domains; failing to stop SMU control before manual writes can cause contention. RPM conversion can overflow without the explicit `speed > UINT_MAX/8` check. PWM conversion depends on `FMAX_DUTY100` being nonzero. Thermal threshold clamping depends on valid PPTable shutdown temperature. Comments reference older ASIC families, so maintainers must trust register names over comments.

## Test Signals
Runtime tests should verify readable RPM/PWM, manual PWM and RPM writes changing fan behavior, auto mode re-enabling SMU control, hotspot temperature reading plausible values, thermal alert programming not failing at startup, and no SMU fan-control feature errors in logs.
