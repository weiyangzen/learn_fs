# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/inc/hwmgr.h

## Purpose

`hwmgr.h` is the central PowerPlay hardware-manager interface for the AMDGPU power-management stack. It defines the long-lived `struct pp_hwmgr` device state object, backend callback tables, SMU manager callbacks, power-play table callbacks, clock/voltage dependency records, fan and thermal policy structures, and entry points used by the generic PowerPlay lifecycle code.

## Important APIs, Types, And Functions

The major API surfaces are `struct pp_smumgr_func`, `struct pp_hwmgr_func`, `struct pp_table_func`, and `struct pp_hwmgr`. `pp_smumgr_func` abstracts firmware operations such as SMU init/fini/start, firmware loading, SMC message sends, PPTable upload/download, SMC table management, AVFS/fan setup, DPM population, and SMC stop. `pp_hwmgr_func` abstracts ASIC policy operations including backend init, state selection, DPM forcing, display notifications, power gating, fan control, sensor reads, overdrive, power limits, BACO, feature masks, MP1 state, I2C bus ownership, XGMI/DF C-state control, GPU metrics, and gfx state changes. `pp_hwmgr` stores chip identifiers, PP table pointers, power states, function tables, display configuration, fan/thermal state, DPM levels, workload settings, power limits, and delayed SW CTF work.

Declared lifecycle entry points include `hwmgr_early_init`, `hwmgr_sw_init`, `hwmgr_sw_fini`, `hwmgr_hw_init`, `hwmgr_hw_fini`, `hwmgr_suspend`, `hwmgr_resume`, and `hwmgr_handle_task`, plus ASIC init hooks for SMU7, SMU8, Vega12, and Vega20.

## Control Flow And Data Flow

This header contains no function bodies. Runtime control flows through callback tables installed by ASIC-specific hwmgr code. Power-state requests flow from user/display/thermal inputs into `pp_power_state` and `pp_hw_power_state`, through adjustment callbacks, then into SMC table updates, firmware messages, and register programming.

## State And Persistence Behavior

`struct pp_hwmgr` is persistent per-GPU software state. It owns PP table memory, backend-private pointers, current/requested power-state pointers, fan defaults, thermal controller information, DPM forced levels, feature masks, overdrive/workload settings, power limits, display config, and delayed work. Hardware persistence is indirect through callbacks that program SMC firmware, clocks, voltages, fan policy, and power-gating states.

## Dependencies And Integration Points

The header depends on Linux `seq_file` and PowerPlay headers `amd_powerplay.h`, `hardwaremanager.h`, `hwmgr_ppt.h`, `ppatomctrl.h`, `power_state.h`, and `smu_helper.h`. It integrates with ASIC hwmgr implementations, SMU manager code, AtomBIOS PP table parsing, display-manager clock requests, thermal/interrupt code, sysfs/debugfs reporting, suspend/resume, reset, and metrics paths.

## Risks And Edge Cases

Callback-table ABI drift is the main risk. A missing or mismatched ASIC callback can break only one generation at runtime. Flexible arrays require correct allocation sizing. Units differ across fields, including kHz/MHz, millivolts, VID encoding, centigrade scales, PWM percent, and RPM. `workload_prority` is misspelled but part of structure layout. `msg_lock` must serialize SMC messages. State pointers must not outlive PP table or backend allocations.

## Test Signals

Useful signals are AMDGPU builds with PowerPlay enabled, probe on SMU7/SMU8/Raven/Vega hardware, power-state transitions, forced DPM sysfs operations, display hotplug and watermark changes, fan PWM/RPM control, thermal throttling and SW CTF, BACO entry/exit, suspend/resume, GPU reset, SMU firmware reload, overdrive edits, power-limit updates, and GPU metrics reads.
