<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi.c

## Purpose
This MSI WMI hotkeys driver handles MSI and MSI Wind WMI events and optionally exposes a vendor WMI backlight device.

## Important APIs, Types, And Functions
The driver uses BIOS GUID `551A1F84-FBDD-4125-91DB-3EA8F44F1D45`, MSI event GUID `B6F3EEF2-3D2F-49DC-9DE3-85BCE18C62F2`, and Wind event GUID `5B3CC38A-40D9-7245-8AE6-1145B751BE3F`. `msi_wmi_keymap` maps generic brightness/volume/mute and Wind turbo/eco events, ignoring keys handled elsewhere. `msi_wmi_query_block()` and `msi_wmi_set_block()` implement WMI data-block access. `bl_get()`/`bl_set_status()` implement six-level backlight mapping. `msi_wmi_notify()` reports sparse key events and suppresses duplicate GPE storms for one event GUID.

## Control Flow
Module init searches for an event GUID, registers input and notify handler for the first match, then registers a WMI backlight if the BIOS GUID exists and ACPI video says vendor backlight should be used. If neither hotkeys nor backlight are present, init fails. Cleanup removes the notify handler, input device, and backlight.

## State And Persistence
Global state tracks selected event GUID metadata, last event timestamp, input device, and backlight device. Brightness state lives in firmware and is mapped through `backlight_map`.

## Dependencies And Integration Points
Dependencies include legacy WMI query/set/notify APIs, input sparse-keymap, backlight core, ACPI video backlight detection, and kernel time helpers. Userspace sees input events and optionally `/sys/class/backlight/msi-wmi`.

## Risks And Edge Cases
Duplicate suppression ignores events within 50 ms for the MSI event GUID because one keypress can generate many GPEs. Brightness key events are suppressed when ACPI video should handle them unless this driver owns backlight. Init error unwind only unregisters input if `event_wmi` was set, so failures before assignment require careful review.

## Test Signals
Tests should cover both event GUID families, duplicate suppression timing, unknown event logging, brightness map get/set, ACPI video backlight gating, absence of BIOS/event GUIDs, and cleanup after partial initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/msi-wmi.c -->
