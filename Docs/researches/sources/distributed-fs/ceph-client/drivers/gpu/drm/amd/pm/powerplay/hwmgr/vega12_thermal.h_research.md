# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega12_thermal.h

`vega12_thermal.h` is the public header for Vega12 thermal and fan-control helpers. It defines temperature limits, fan mode constants, a multi-sensor temperature container, and the thermal/fan functions consumed by `vega12_hwmgr.c`.

`struct vega12_temperature` contains edge, hotspot, HBM, VR, liquid, and PLX temperature fields. Constants define alert masks, minimum/maximum readings, valid alert thresholds, and static PWM mode IDs. The declared functions cover temperature reads, thermal controller start/stop, alert disable, fan speed information, fan RPM reads, fan reset, and SMC fan-control start/stop.

There is no executable control flow or stored state in this header. The APIs act on `struct pp_hwmgr`, whose backend and PPTable carry thermal limits and fan target configuration. It depends on `hwmgr.h` for `struct pp_hwmgr`, `struct PP_TemperatureRange`, and fan speed info types.

Risks are stale declarations when implementation behavior changes and unused structures/constants drifting away from SMU metric fields. Test signals are clean compilation of all hwmgr users and runtime coverage of every exported thermal/fan callback.
