# sources/distributed-fs/ceph-client/drivers/platform/x86/dasharo-acpi.c

Purpose: Dasharo ACPI hwmon driver for ACPI ID `DSHR0001`, exposing firmware-defined temperature, fan tachometer, and fan PWM channels.

Important APIs/types/functions: `struct dasharo_data` stores per-feature capability lists. `dasharo_get_feature_cap_count()` calls ACPI `GFCP`; `dasharo_read_channel()` calls `GTMP`, `GFTH`, or `GFDC`; hwmon callbacks implement read, label read, and visibility filtering.

Control flow/state/persistence: Probe allocates state, enumerates capabilities across feature/group pairs, and registers a fixed 24-channel hwmon description with visibility determined by discovered counts. Sensor values are read live from ACPI; there is no write path or persistent driver state beyond the capability cache.

Dependencies/integration: ACPI platform driver, hwmon core, `devm_hwmon_device_register_with_info()`, and temperature unit conversion to millidegrees.

Risks/test signals: Firmware returning unknown groups may produce missing labels; capability counts are capped at 24. Test visible channel counts against `GFCP`, labels, ACPI failure handling, and value scaling for temp/fan/pwm.
