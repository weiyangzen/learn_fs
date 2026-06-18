# sources/distributed-fs/ceph-client/include/linux/regulator/tps51632-regulator.h

Purpose: this header provides legacy platform data for the TI TPS51632 D-CAP step-down controller with serial VID and DVFS support.

Important APIs/types/functions: it declares `struct tps51632_regulator_platform_data`, containing `reg_init_data`, `enable_pwm_dvfs`, `dvfs_step_20mV`, `max_voltage_uV`, and `base_voltage_uV`. There are no functions or macros beyond include guards.

Control flow: board/platform code fills this structure before regulator driver probe. The driver then uses it to decide whether PWM-DVFS is enabled, whether DVFS steps are 10 mV or 20 mV, and how to calculate voltage limits from base and maximum microvolt values. Runtime sequencing is delegated to the regulator core and the chip driver.

State and persistence: this is initialization data only. Persistent state is either board firmware data or regulator constraints; no mutable state is stored in the header.

Dependencies and integration points: it depends on `struct regulator_init_data` and `bool` being visible to includers, and integrates with NVIDIA-era platform files and the TPS51632 regulator driver.

Risks: platform-data configuration can conflict with actual board wiring or voltage tables, especially when PWM-DVFS step mode is wrong. Test signals include driver probe with platform data, DVFS voltage transition tests, regulator constraint validation, and compile coverage for platform builds that still include this header.
