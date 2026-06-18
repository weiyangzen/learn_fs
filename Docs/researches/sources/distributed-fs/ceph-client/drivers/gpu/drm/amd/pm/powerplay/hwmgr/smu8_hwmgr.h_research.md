# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu8_hwmgr.h

Purpose: defines the SMU8 backend data model, constants, DPM state structures, display PHY argument packing, and the public function-pointer initialization hook.

Important APIs/types: `struct smu8_dpm_entry` stores soft/hard min/max clocks; `struct smu8_sys_info` mirrors AtomBIOS integrated system data; `DDI_POWERGATING_ARG()` packs PHY/lane/RX/TX/core fields; `struct smu8_power_level` and `struct smu8_power_state` hold per-power-state clock/voltage/divider/NB/BAPM/action data; `struct smu8_hwmgr` stores the backend lifetime state. DPM flag constants mirror enabled SMC features.

Control flow and state: generic `pp_hw_power_state` objects are cast to SMU8-specific states by `magic`. `struct smu8_hwmgr` persists across backend lifetime and tracks BIOS data, requested/current power states, DPM limits, power-gate booleans, CC6, PowerTune flags, boot levels, display state, CAC buffer addresses, and max SCLK cache.

Dependencies and integration: includes `cgs_common.h` and `ppatomctrl.h`, and relies on powerplay types defined elsewhere. Consumed primarily by `smu8_hwmgr.c` and generic powerplay callbacks.

Risks and test signals: field layout is a shared state contract; fixed-size arrays depend on BIOS/SMU counts; similar policy flags can be misinitialized. Test state casts, maximum-level parsing, and compile all SMU8 users.
