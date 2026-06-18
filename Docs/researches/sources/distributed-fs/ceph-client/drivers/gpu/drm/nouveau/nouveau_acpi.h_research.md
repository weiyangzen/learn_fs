# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_acpi.h

## Purpose

This header declares Nouveau's ACPI helper API and provides no-op/static fallback implementations when ACPI-on-x86 support is not compiled in.

## Important APIs, Types, and Functions

It defines `ROM_BIOS_PAGE` and declares or stubs `nouveau_is_optimus`, `nouveau_is_v1_dsm`, `nouveau_register_dsm_handler`, `nouveau_unregister_dsm_handler`, `nouveau_switcheroo_optimus_dsm`, `nouveau_acpi_edid`, `nouveau_acpi_video_backlight_use_native`, and `nouveau_acpi_video_register_backlight`.

## Control Flow

Including code can call the helpers unconditionally. On supported builds calls dispatch to `nouveau_acpi.c`; otherwise detection returns false, EDID returns `NULL`, native backlight preference returns true, and registration hooks are empty.

## State and Persistence Behavior

The header itself stores no state. Runtime ACPI detection state is private to the implementation file.

## Dependencies and Integration Points

It is used by Nouveau device registration, switcheroo/power-management paths, EDID retrieval, and backlight setup.

## Risks

Fallback semantics must remain conservative. A wrong `nouveau_acpi_video_backlight_use_native` default would suppress the driver's native backlight on non-ACPI builds.

## Test Signals

Build with and without `CONFIG_ACPI`/`CONFIG_X86`, test Optimus detection consumers, and validate backlight/EDID fallback behavior.
