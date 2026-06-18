# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu7_thermal.h

Purpose: declares SMU7 thermal and fan-control callbacks and shared constants.

Important APIs/types: defines thermal high/low alert masks, legal temperature reading/alert ranges, static PWM and static RPM FDO modes, and declares temperature read, thermal start/stop/uninitialize, alert disable, SMC fan-control start/stop, fan speed info, PWM/RPM read/write, static/default mode switching, and fan reset helpers.

Control flow and state: used by SMU7 backend function tables and sysfs/OverDrive fan operations. The header declares behavior; runtime state is stored by `pp_hwmgr` and SMC/hardware registers in the C implementation.

Dependencies and integration: includes `hwmgr.h` for `pp_hwmgr`, `phm_fan_speed_info`, and `PP_TemperatureRange`. Callers must pass temperatures in `PP_TEMPERATURE_UNITS_PER_CENTIGRADES`.

Risks and test signals: manual fan controls must respect fan presence and RPM capability. Test compile coverage, valid/invalid thermal ranges, fan mode reset, and PWM/RPM capability reporting.
