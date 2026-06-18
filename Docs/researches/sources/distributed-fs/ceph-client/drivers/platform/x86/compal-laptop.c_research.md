# sources/distributed-fs/ceph-client/drivers/platform/x86/compal-laptop.c

Purpose: Compal/Dell Mini platform driver built around ACPI EC register access. It exposes vendor backlight, rfkill, and optional wakeup, hwmon fan/temperature, and battery power_supply support on DMI-approved systems.

Important APIs/types/functions: `struct compal_data` caches fan PWM state and battery identity strings. EC helpers (`ec_read_u8`, `ec_read_u16`, `ec_read_sequence`, `set_backlight_level`, `set_pwm`, `get_fan_rpm`) drive all hardware access. The public integrations are `backlight_ops`, `rfkill_ops`, hwmon sysfs attributes, `power_supply_desc`, and `compal_driver`.

Control flow/state/persistence: `compal_init()` checks ACPI and DMI unless `force=1`, registers vendor backlight when ACPI video selects vendor control, creates the platform device, and registers Wi-Fi/Bluetooth rfkill. `compal_probe()` only creates wakeup, hwmon, and battery interfaces when `extra_features` is set by DMI. Persistent hardware state lives in EC registers; driver memory only caches requested PWM and strings. Removal resets fan control to motherboard mode.

Dependencies/integration: ACPI EC, DMI, backlight, rfkill, hwmon, power_supply, sysfs, and platform-device core. It does not use Dell SMBIOS.

Risks/test signals: EC addresses and the nonlinear PWM table are model-specific; `force=1` can be unsafe. Test module load/unload, backlight brightness/power, rfkill polling/set, hwmon readings, battery properties/charge limit writes, and fan-control reset on unload.
