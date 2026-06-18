# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_thermal.c

## Purpose

This file implements Vega10 thermal controller setup, temperature alert programming, fan speed reporting and manual control, SMC fan-control table updates, and multi-GPU fan boost behavior for the AMD PowerPlay hwmgr.

## Important APIs, Types, and Functions

Public functions include `vega10_fan_ctrl_get_fan_speed_info`, PWM and RPM get/set helpers, `vega10_fan_ctrl_set_static_mode`, `vega10_fan_ctrl_set_default_mode`, `vega10_fan_ctrl_reset_fan_speed_to_default`, `vega10_fan_ctrl_start_smc_fan_control`, `vega10_fan_ctrl_stop_smc_fan_control`, `vega10_thermal_get_temperature`, `vega10_thermal_disable_alert`, `vega10_thermal_stop_thermal_controller`, `vega10_start_thermal_controller`, `vega10_thermal_ctrl_uninitialize_thermal_controller`, and `vega10_enable_mgpu_fan_boost`. Internal helpers toggle the `GNLD_FAN_CONTROL` and `GNLD_FW_CTF` SMC features, initialize tach/PWM registers, program interrupt thresholds, and write fan parameters into the SMC PPTable.

## Control Flow, State, and Persistence

Fan capability reporting is based on `hwmgr->thermal_controller.fanInfo`, no-fan flags, tachometer pulses, and `PHM_PlatformCaps_FanSpeedInTableIsRPM`. PWM reads convert `FDO_PWM_DUTY` against `FMAX_DUTY100` to a 0-255 value. RPM reads use `PPSMC_MSG_GetCurrentRpm` when SMC fan control is supported, otherwise compute from `CG_TACH_STATUS` and ASIC xclk.

Manual PWM/RPM writes stop microcode fan control when needed, program static duty or target tach period, and switch `CG_FDO_CTRL2` into static PWM or static RPM mode. The original default PWM mode and `TMIN` are cached in `hwmgr->fan_ctrl_default_mode`, `hwmgr->tmin`, and `hwmgr->fan_ctrl_is_in_default_mode` so default mode can be restored.

Thermal startup initializes tach response, programs alert min/max using the caller range and PowerTune shutdown temperature, enables FW CTF and interrupt clear bits, writes fan table fields into `data->smc_state_table.pp_table`, pushes the PPTABLE to SMC, and starts SMC fan control if microcode fan control remains enabled. Stop paths disable alerts and restore/default fan control.

## Dependencies and Integration Points

The file depends on SOC15 THM registers, AMDGPU xclk, SMC messages and table manager, Vega10 SMC feature bookkeeping, thermal/fan values parsed by `vega10_processpptables.c`, and hwmgr function tables in `vega10_hwmgr.c`. It updates the SMC PPTable consumed by firmware and exposes fan/thermal operations to the PowerPlay public interface.

## Risks and Test Signals

Risk areas include divide-by-zero guards around tach/PWM values, restoring `TMIN` with the expected field encoding, signed/unsigned temperature conversions, no-fan behavior returning mixed `0` and negative errors, stopping microcode control before manual writes, and restart sequencing after mGPU boost. Tests should cover no-fan boards, boards without `GNLD_FAN_CONTROL`, RPM bounds, PWM saturation at 255, invalid temperature ranges, FW CTF enable/disable failures, SMC table-manager failures, and default-mode restoration after manual control.
