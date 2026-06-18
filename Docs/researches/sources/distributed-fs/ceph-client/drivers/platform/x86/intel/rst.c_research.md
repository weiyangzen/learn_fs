# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/rst.c

## Purpose

This driver exposes Intel Rapid Start Technology ACPI controls through two sysfs attributes on the matched ACPI companion device.

## Important APIs, Types, And Functions

`irst_show_wakeup_events()` and `irst_store_wakeup_events()` wrap ACPI methods `GFFS` and `SFFS`. `irst_show_wakeup_time()` and `irst_store_wakeup_time()` wrap `GFTV` and `SFTV`. Probe creates `wakeup_time` and `wakeup_events` device attributes, and remove deletes them.

## Control Flow

The platform driver matches ACPI ID `INT3392`. Probe creates `wakeup_time` first, then `wakeup_events`; failure to create the second rolls back the first. User reads evaluate ACPI integer methods; user writes parse an unsigned long and execute the matching ACPI simple method.

## State And Persistence

The driver stores no private state. Values persist only through firmware/ACPI state managed by platform firmware.

## Dependencies And Integration Points

It depends on ACPI companion devices, platform driver binding, and sysfs device attributes. The interface is firmware-defined through four ACPI methods.

## Risks

The attributes are mode `0600`, limiting access to privileged users, but values are passed directly to firmware after numeric parsing. ACPI method absence or firmware failure is collapsed to `-EINVAL`, which can obscure diagnostics. The code uses `sprintf()` rather than `sysfs_emit()`, matching older style but less preferred.

## Test Signals

Probe on `INT3392`, existence of both sysfs files, successful reads/writes against known firmware, rollback on attribute creation failure, and clean remove are the key signals.
