# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.c

Purpose: implements SMU7 thermal controller and fan-control operations: temperature reads, high/low alert programming, SMC fan control, manual PWM/RPM control, and default fan restoration.

Important APIs and functions: `smu7_fan_ctrl_get_fan_speed_info()` reports percentage and RPM support. PWM/RPM read functions inspect SMC indirect thermal/tach registers. `smu7_fan_ctrl_set_static_mode()` caches default FDO mode and `TMIN`, then switches to static fan mode; `smu7_fan_ctrl_set_default_mode()` restores them. `smu7_fan_ctrl_start_smc_fan_control()` selects fuzzy/table fan policy, sets max output, target temperature, and Zero RPM on supported Polaris ASICs. `smu7_start_thermal_controller()` initializes tach/FDO settings, programs temperature range, enables alerts, enables AVFS, uploads fan tables, and starts SMC fan control.

Control flow and state: manual fan writes stop microcode fan control, compute duty or tach target period, program hardware, and set static mode. Controller stop disables thermal alerts and restores default fan mode. State is cached in `pp_hwmgr` (`fan_ctrl_default_mode`, `tmin`, `fan_ctrl_is_in_default_mode`, `fan_ctrl_enabled`) while thresholds and fan control live in SMC registers/firmware.

Dependencies and integration: uses PHM register macros, `smum_send_msg_to_smc*`, thermal AVFS/fan-table SMC helpers, platform caps, `amdgpu_asic_get_xclk()`, and SMU7 hwmgr thermal data.

Risks and test signals: tach and duty math depends on nonzero hardware counters; RPM set rejects invalid bounds. `fan_ctrl_enabled` can be set despite late SMC failure. Test PWM/RPM sysfs, no-fan paths, thermal interrupts, Zero RPM, AVFS enable failure, suspend/resume, and default fan restoration.
