# sources/distributed-fs/ceph-client/drivers/platform/x86/ayaneo-ec.c

## Purpose
`ayaneo-ec.c` is a DMI-gated platform driver for AYANEO handheld EC features. Depending on board quirks, it exposes fan monitoring/control through hwmon, battery charge-inhibit control through a power-supply extension, and AYANEO 3 magic-module controller power/status through sysfs.

## Important APIs, Types, And Functions
`struct ayaneo_ec_quirk` selects feature availability. `struct ayaneo_ec_platform_data` stores the platform device, quirks, battery hook, hwmon mutex, and restore flags for charge limit and PWM. The DMI table maps specific AYANEO board names to fan-only, fan-plus-charge, or AYANEO 3 feature sets.

Hwmon callbacks `ayaneo_ec_read()` and `ayaneo_ec_write()` use `ec_read()` and `ec_write()` against fixed EC registers for fan RPM, PWM value, and PWM mode. The power-supply extension callbacks map `POWER_SUPPLY_PROP_CHARGE_BEHAVIOUR` to EC values `0xaa` for auto and `0x55` for inhibit. `controller_power_*` and `controller_modules_show()` expose controller power and left/right module connection state.

## Control Flow
Module init creates a platform bundle. Probe checks DMI, allocates data, initializes the mutex, and conditionally registers an hwmon device and a battery hook. The driver-level `dev_groups` always points to the magic-module attribute group, but `aya_mm_is_visible()` hides those files unless the DMI quirk advertises magic modules.

Freeze records whether charge inhibit and manual PWM were active. If manual fan control was active, it switches the EC back to auto before hibernation to reduce overheat risk if resume fails. Restore reapplies charge inhibit when needed; PWM restoration is deliberately deferred until the next PWM write by userspace.

## State And Persistence
The EC is the source of truth for fan, charge, power, and module state. Kernel state records quirk selection and two restore booleans across hibernation. `restore_pwm` is protected by `hwmon_lock` because writes can race with PM state. Charge-inhibit state can be restored after hibernation, while manual PWM is not immediately restored for safety.

## Dependencies And Integration Points
The driver integrates with the ACPI EC accessors, DMI matching, hwmon, power-supply extension APIs, ACPI battery hooks, sysfs attribute groups, platform devices, and PM freeze/restore callbacks.

## Risks
All EC registers are hardcoded per AYANEO firmware convention; wrong DMI matching can expose writes on unsupported hardware. PWM conversion loses precision between 0-255 hwmon and 0-100 EC units. `ayaneo_psy_prop_is_writeable()` returns true for any queried property, relying on the property list and set callback to reject unsupported values. Manual fan mode is intentionally not restored immediately after hibernation, which may surprise users but avoids thermal risk.

## Test Signals
Validate DMI feature gating on each listed board, hwmon fan RPM and PWM mode/value reads, PWM write bounds and conversion, charge behavior get/set through the battery extension, hibernation freeze/restore behavior for charge inhibit and manual PWM, AYANEO 3 controller power toggling, module-state string mapping, and unload of the platform bundle.
