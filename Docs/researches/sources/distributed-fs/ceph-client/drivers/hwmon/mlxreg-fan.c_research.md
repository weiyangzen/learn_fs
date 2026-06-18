# `sources/distributed-fs/ceph-client/drivers/hwmon/mlxreg-fan.c` Research

Purpose: this platform hwmon driver exposes Mellanox/NVIDIA platform fan tachometers and PWM controls described by `mlxreg_core_platform_data`. It also registers thermal cooling devices for connected PWM outputs when thermal support is available.

Important APIs, types, and functions: `struct mlxreg_fan_tacho` stores tachometer register, fault mask, presence register, and shift. `struct mlxreg_fan_pwm` stores PWM register and thermal/hwmon state. `struct mlxreg_fan` stores regmap, platform data, arrays for up to 24 tachos and four PWMs, tachos-per-drawer, samples, and divider. `mlxreg_fan_read()`/`write()` implement hwmon. `_mlxreg_fan_set_cur_state()` arbitrates thermal and hwmon PWM state. `mlxreg_fan_config()` parses platform data labels `tacho`, `pwm`, and `conf`.

Control flow: probe reads platform data, configures connected tachos/PWMs and speed formula parameters, registers hwmon, then optionally registers a cooling device per PWM. Fan reads first check presence per drawer, then read tach register and return zero for absent or faulted values; otherwise RPM is calculated from register value, divider, and sample count. PWM writes enforce 20-100 percent duty and, when thermal is enabled, only lower hardware speed if the hwmon-requested state is not below thermal-requested state.

State and persistence: hardware registers store tach/PWM values and capabilities. Driver state records discovered connectivity and last hwmon/thermal states. There is no periodic cache.

Dependencies and integration points: depends on platform data from Mellanox regmap core, regmap, hwmon, optional thermal framework, and platform driver alias `mlxreg-fan`.

Risks and test signals: risks include parsing platform data by substring, a likely bounds typo comparing `pwm_num == MLXREG_FAN_MAX_TACHO` instead of max PWM, presence bit math with `rol32(channel, shift) / tachos_per_drwr`, and arbitration between thermal and hwmon. Tests should cover invalid/duplicate config labels, capability-based connection filtering, drawer/tacho validation, PWM-not-connected handling, duty/state conversions, thermal arbitration, and RPM formula edge cases for fault/min/max register values.
