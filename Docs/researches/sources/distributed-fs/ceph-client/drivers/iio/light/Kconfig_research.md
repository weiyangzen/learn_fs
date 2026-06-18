# sources/distributed-fs/ceph-client/drivers/iio/light/Kconfig

## Purpose

This Kconfig menu declares the build-time configuration surface for IIO light, color, UV, proximity, and related combo sensors. It maps each driver to its bus and helper dependencies, selects common IIO buffer/trigger/regmap/GTS support where needed, and provides module names for users and distributions.

## Important APIs, Types, and Functions

The file is declarative Kconfig rather than C code. The subset entries include `ACPI_ALS`, `ADJD_S311`, `ADUX1020`, `AL3000A`, `AL3010`, `AL3320A`, `APDS9160`, `APDS9300`, `APDS9306`, `APDS9960`, and `AS73211`. Important dependency selectors include `depends on I2C`, `depends on ACPI`, `select REGMAP_I2C`, `select IIO_BUFFER`, `select IIO_TRIGGERED_BUFFER`, `select IIO_KFIFO_BUF`, and `select IIO_GTS_HELPER`.

## Control Flow

Kernel configuration tools present the "Light sensors" menu. Selecting a tristate symbol controls whether the matching object in the directory Makefile is omitted, built-in, or compiled as a module. `select` clauses pull in helper infrastructure needed by the driver implementation, while `depends on` clauses hide entries when the required bus or parent subsystem is unavailable.

## State and Persistence Behavior

The persistent state is the generated kernel `.config` and module build result. There is no runtime state here, but incorrect dependencies persist into build failures or missing runtime functionality.

## Dependencies and Integration Points

This file integrates with `drivers/iio/light/Makefile`, the IIO core, I2C, ACPI, HID sensor hub support, MFD parents, regmap backends, triggered buffers, kfifo buffers, and the IIO gain-time-scale helper. Its ordering comment asks new entries to stay alphabetic, which keeps menu and Makefile maintenance predictable.

## Risks and Edge Cases

Kconfig `select` bypasses dependency checks of the selected symbol, so entries must only select helpers that are safe to force-enable. Missing `REGMAP_I2C`, buffer, trigger, or GTS selections can produce link failures or incomplete driver behavior. This snapshot contains minor text issues such as duplicated help lines in unrelated entries; those are not runtime bugs but are maintenance signals.

## Test Signals

Run representative `allyesconfig`, `allmodconfig`, and focused builds for each listed symbol as built-in and module. Verify module names match help text and Makefile object names, and run dependency-disabled configs such as no I2C or no ACPI to confirm symbols are hidden as expected.
