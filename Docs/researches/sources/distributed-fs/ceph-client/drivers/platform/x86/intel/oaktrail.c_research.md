<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/oaktrail.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/oaktrail.c

## Purpose
Legacy Intel OakTrail platform extras driver. It exposes EC-backed rfkill controls for WiFi, Bluetooth, GPS, and WWAN, and optionally a vendor backlight device.

## Important APIs, Types, And Functions
`oaktrail_rfkill_set()` reads EC device-state byte `0xd6`, toggles a radio bit, and writes it back. `oaktrail_rfkill_new()` allocates and registers rfkill devices. Backlight callbacks read/write EC brightness address `0x44` and control address `0x3a`. Module parameter `force` bypasses DMI gating.

## Control Flow
Module init requires ACPI and either DMI match `OakTrail platform` or `force=1`. It registers a platform driver/device, registers vendor backlight only when ACPI video selected vendor backlight type, then creates four rfkill devices. Cleanup unregisters backlight, rfkills, device, and driver.

## State And Persistence
Global pointers track the platform device, backlight, and rfkill devices. Hardware state persists in EC registers and is directly modified by callbacks.

## Dependencies And Integration Points
Depends on ACPI EC read/write helpers, DMI, rfkill, backlight, ACPI video backlight policy, platform device APIs, and module parameters.

## Risks And Test Signals
Risks include fixed EC offsets, weak rfkill initial-state expression, unconditional backlight cleanup even if not registered, and broad `force` usage. Test on OakTrail hardware for radio toggles, backlight brightness 0-100, DMI gating, unload paths, and ACPI video backlight coexistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/oaktrail.c -->
