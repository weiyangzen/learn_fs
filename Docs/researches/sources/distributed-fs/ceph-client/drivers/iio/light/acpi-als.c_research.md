# sources/distributed-fs/ceph-client/drivers/iio/light/acpi-als.c

## Purpose

`acpi-als.c` exposes ACPI0008 ambient light readings through IIO. It currently supports illuminance via the ACPI `_ALI` method and provides both direct reads and a triggered buffer path driven by ACPI notifications.

## Important APIs, Types, and Functions

- `struct acpi_als` stores the ACPI companion, a mutex, and the private IIO trigger.
- `acpi_als_read_value()` evaluates ACPI integer methods such as `_ALI`.
- `acpi_als_read_raw()` returns `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_PROCESSED` for the single `IIO_LIGHT` channel.
- `acpi_als_notify()` receives `ACPI_ALS_NOTIFY_ILLUMINANCE` and polls the private trigger when the buffer uses that trigger.
- `acpi_als_trigger_handler()` reads `_ALI` and pushes `{s32 light, timestamp}`.
- `acpi_als_probe()` allocates the IIO device, trigger, triggered buffer, and ACPI notify handler; `acpi_als_remove()` unregisters the notify handler.

## Control Flow

Probe binds to ACPI ID `ACPI0008`, creates one light channel plus timestamp, registers a trigger, assigns it as the default trigger, sets up a triggered buffer, registers the IIO device, then installs the ACPI device notify handler. Direct sysfs reads call `_ALI` synchronously. Notification events only produce buffered samples when the IIO buffer is enabled and the device is using its own trigger.

## State and Persistence Behavior

The driver stores no calibration or cached sensor values. The mutex serializes trigger-handler reads. The ACPI notify registration persists from probe to remove, and devm resources handle IIO objects.

## Dependencies and Integration Points

It depends on ACPI evaluation/notification APIs, platform-device ACPI companion matching, IIO core, triggers, triggered buffers, and kfifo buffer support selected by Kconfig.

## Risks and Edge Cases

Only `_ALI` is implemented although ACPI0008 can describe chromaticity, color temperature, polling intervals, and response tables. Firmware evaluation failure becomes `-EIO`. Notifications are ignored when buffering is disabled or another trigger is active, which is correct but can surprise platform debugging.

## Test Signals

Test ACPI0008 probe, direct raw/processed reads, ACPI method failure, notification-driven buffer samples, timestamp population, unhandled notify events, and remove-time notify cleanup.
