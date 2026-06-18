# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-gx-socinfo.c

## Purpose
This initcall decodes Amlogic Meson GX and newer SoC ID registers and registers a Linux `soc_device` with family, SoC/package ID, and revision strings.

## Important APIs, Types, And Functions
Static tables `soc_ids[]` and `soc_packages[]` map major/package fields to marketing names. Inline helpers extract major, minor, package, and misc fields from `socinfo`. `socinfo_to_soc_id()` and `socinfo_to_package_id()` perform table lookup. `meson_gx_socinfo_init()` does all registration.

## Control Flow
At device initcall time, the code finds the `amlogic,meson-gx-ao-secure` syscon node, verifies availability and `amlogic,has-chip-id`, obtains a regmap, reads `AO_SEC_SOCINFO_OFFSET`, allocates `soc_device_attribute`, formats revision and SoC ID strings, registers with `soc_device_register()`, and logs the detected chip.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated strings. Dependencies include OF, syscon/regmap, bitfield helpers, and `SOC_BUS`.

## Integration Points
Userspace sees the decoded information under sysfs soc device attributes. Other kernel paths may use soc_bus matching. The Kconfig option selects `SOC_BUS` and builds this bool driver on ARM64 Meson platforms.

## Risks
Unknown IDs fall back to `"Unknown"` rather than failing, which preserves boot but can reduce diagnostics. String allocation failures after `soc_dev_attr` allocation are not explicitly checked before registration. The table must be updated for new package IDs.

## Test Signals
Boot on known GX/G12/SM/C/S parts, inspect `/sys/devices/soc*`, verify unknown-ID fallback, and test missing/disabled/no-chip-id DT nodes returning `-ENODEV`.
