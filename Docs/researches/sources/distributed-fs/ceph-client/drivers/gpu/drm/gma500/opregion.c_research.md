# sources/distributed-fs/ceph-client/drivers/gpu/drm/gma500/opregion.c

## Purpose
This file implements Intel graphics OpRegion support for GMA500. It maps the ACPI OpRegion, exposes ACPI/ASLE mailboxes, acknowledges ACPI video notifications, and handles ASLE backlight requests from firmware.

## Important APIs, Types, and Functions
Public functions are `psb_intel_opregion_setup()`, `psb_intel_opregion_init()`, `psb_intel_opregion_fini()`, `psb_intel_opregion_enable_asle()`, and `psb_intel_opregion_asle_intr()`. Local ABI structs model the OpRegion header, ACPI mailbox, SWSCI placeholder, and ASLE mailbox. `asle_set_backlight()` translates ASLE brightness to `gma_backlight_set()`, and `psb_intel_opregion_asle_work()` services ASLE requests.

## Control Flow
Setup reads PCI config `ASLS`, maps 8 KiB with `acpi_os_ioremap()`, validates the `"IntelGraphicsMem"` signature, records header/VBT/lid pointers, and attaches ACPI/ASLE mailbox pointers based on header mailbox bits. Init sets ACPI driver-ready flags and registers an ACPI notifier. ASLE interrupts schedule work, which checks command bits and handles supported backlight updates. Fini clears readiness, unregisters the notifier, cancels work, and unmaps the OpRegion.

## State and Persistence Behavior
Mapped OpRegion pointers live in `dev_priv->opregion`; `system_opregion` is a global pointer used by the ACPI notifier. ASLE work is deferred through `opregion.asle_work`. The code writes firmware-visible readiness/status/brightness fields such as `drdy`, `csts`, `ardy`, `tche`, `aslc`, and `cblv`.

## Dependencies and Integration Points
It integrates with ACPI, PCI config space, DRM debug logging, GMA interrupt handling (`psb_intel_opregion_asle_intr()`), pipe status enabling, and backlight control. BIOS parsing can also consume `opregion.vbt`.

## Risks
Only ASLE backlight is implemented; ALS, panel fitting, and PWM frequency requests are advertised but not serviced. `system_opregion` assumes one relevant device. Duplicate macro definitions make maintenance noisy. Mapping and mailbox offsets must match firmware exactly. ASLE enable is skipped on non-PC-like Medfield behavior only by comments and the `system_opregion` condition.

## Test Signals
Signals include valid OpRegion signature detection, ACPI mailbox readiness flags set/cleared on init/fini, ACPI video notifier acknowledgments, ASLE backlight requests changing brightness and updating `cblv`, and clean unmap/cancel-work during unload.
