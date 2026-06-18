# sources/distributed-fs/ceph-client/drivers/acpi/sleep.h

## Purpose

This internal header shares ACPI sleep and wake coordination declarations between the sleep implementation and other ACPI core files. It exposes wake-device list locks, power-resource resume, waking-vector setup, and s2idle hooks without exporting the full implementation details of `sleep.c`.

## Important APIs, types, and functions

The header declares `acpi_enable_wakeup_devices()`, `acpi_disable_wakeup_devices()`, `acpi_check_wakeup_handlers()`, `acpi_wakeup_device_list`, `acpi_device_lock`, `acpi_resume_power_resources()`, `acpi_set_waking_vector()`, all ACPI s2idle callbacks, and `acpi_s2idle_setup()`. It also exposes `acpi_sleep_default_s3`, with a compile-time default of true when `CONFIG_ACPI_SLEEP` is disabled.

## Control flow

There is no runtime control flow except the inline `acpi_set_waking_vector()`, which forwards a 32-bit wakeup address to `acpi_set_firmware_waking_vector()` with a zero 64-bit vector. Callers in sleep, scan, and wakeup code use the declarations to prepare and tear down wake state around PM transitions.

## State and persistence

The header declares, but does not allocate, the wakeup device list and ACPI device lock. `acpi_sleep_default_s3` reflects either runtime DMI/boot policy from `sleep.c` or a constant fallback when sleep support is absent.

## Dependencies and integration points

It integrates ACPI scan/wakeup code with the PM implementation. The declarations depend on ACPICA types such as `acpi_status` and Linux list/mutex definitions included by consumers.

## Risks

Because this is an internal contract, signature drift must be synchronized with `sleep.c`, wakeup-device code, and scan/power-resource users. The inline waking-vector wrapper is architecture-sensitive; changing its argument handling can break S3 resume.

## Test signals

Build coverage under `CONFIG_ACPI_SLEEP`, `CONFIG_SUSPEND`, and reduced PM configurations is the main signal, plus suspend/resume tests that validate wakeup device enablement and firmware waking-vector setup.
