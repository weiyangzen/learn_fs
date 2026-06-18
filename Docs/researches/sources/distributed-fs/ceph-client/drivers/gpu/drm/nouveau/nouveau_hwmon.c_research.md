
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_hwmon.c

## Purpose
Registers Nouveau with the Linux hwmon subsystem and exposes GPU temperature, fan, PWM, voltage, and power readings/controls when the corresponding NVKM subdevices support them.

## Important APIs, Types, and Functions
External lifecycle functions are `nouveau_hwmon_init()` and `nouveau_hwmon_fini()`. Visibility callbacks include `nouveau_chip_is_visible()`, `nouveau_temp_is_visible()`, `nouveau_fan_is_visible()`, `nouveau_input_is_visible()`, `nouveau_pwm_is_visible()`, and `nouveau_power_is_visible()`. Read/write callbacks include `nouveau_read()`, `nouveau_write()`, channel-specific read/write helpers, and `nouveau_read_string()`. Extra sysfs attributes cover fan PWM min/max and automatic fan boost threshold/hysteresis.

## Control Flow
Initialization checks for thermal, voltage, or iccsense subdevices. If none exist, it skips registration. If thermal attributes and fan control exist, it attaches additional legacy-style sysfs groups. It then registers `hwmon_device_register_with_info()` with `nouveau_chip_info`. The hwmon core calls visibility callbacks to expose only supported attributes, then read/write callbacks translate hwmon requests into NVKM therm/volt/iccsense operations. Runtime power-off state causes live sensor reads to return `-EINVAL` rather than waking or touching an off device.

## State and Persistence
Persistent state is a small `struct nouveau_hwmon` allocated on init and stored in `drm->hwmon`, containing the DRM device and registered hwmon device. Sensor values and thresholds persist in hardware/NVKM subdevices, not in this file.

## Dependencies and Integration Points
Depends on Linux hwmon, hwmon-sysfs, power supply includes, and NVKM `therm`, `volt`, and `iccsense` subdevices accessed through `nvxx_*` helpers. It is called from `nouveau_drm_device_init()` and `nouveau_drm_device_fini()`.

## Risks and Test Signals
Risks include exposing writable thresholds on hardware that cannot safely handle them, reading sensors while runtime suspended, unit conversions between degrees/millivolts/microwatts, and missing capability checks for partially implemented NVKM callbacks. Test signals include sysfs attribute presence by hardware capability, read/write threshold behavior, runtime-suspended reads, fan PWM mode/input writes, iccsense power limits, hwmon unregister on module unload, and builds without `CONFIG_HWMON`.
