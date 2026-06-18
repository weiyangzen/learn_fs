# sources/distributed-fs/ceph-client/drivers/soc/amlogic/meson-mx-socinfo.c

## Purpose
This initcall decodes older Amlogic Meson MX-family SoC identity from assist, bootrom, and optional analog-top syscon registers and registers it with soc_bus.

## Important APIs, Types, And Functions
`meson_mx_socinfo_revision()` maps major, misc, and metal revision values to revision strings. `meson_mx_socinfo_soc_id()` maps major and metal revision to SoC ID strings. `meson_mx_socinfo_init()` performs syscon lookup, register reads, root model lookup, attribute allocation, and registration.

## Control Flow
The initcall obtains regmaps by compatibles for assist and bootrom. It optionally reads the analog-top metal revision if a matching node exists. Then it reads the hardware revision and misc version, allocates attributes, copies the root `model` property into `machine`, formats revision and SoC ID strings, registers the soc device, and logs the result.

## State, Persistence, And Dependencies
State is the registered soc_bus device and allocated strings. Dependencies include syscon/regmap, OF, `SOC_BUS`, and ARM Meson platform configuration.

## Integration Points
It supplies userspace-visible SoC metadata for Meson6, Meson8, Meson8b, and Meson8m2 platforms. It complements the GX socinfo driver for newer ARM64 parts.

## Risks
String allocation failures are not checked before `soc_device_register()`. If analog-top exists but regmap/read fails, init aborts even though base identity could be available. Unknown revisions are normalized to generic or unknown strings.

## Test Signals
Boot on Meson6, Meson8, Meson8b, and Meson8m2 DTs, inspect soc_bus attributes, test missing syscon compatibles, and verify metal revision branches.
