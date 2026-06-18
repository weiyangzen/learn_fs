<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.c

## Purpose
This Lenovo WMI events driver provides a central WMI event subscription point for hardware-triggered Lenovo events. In this file, the implemented event is thermal mode changes from GUID `D320289E-8FEA-41E0-86F9-911D83151B5F`.

## Important APIs, Types, And Functions
The global `events_chain_head` is a blocking notifier chain. Exported APIs are `lwmi_events_register_notifier()`, `lwmi_events_unregister_notifier()`, and `devm_lwmi_events_register_notifier()`, all exported in namespace `LENOVO_WMI_EVENTS`. `struct lwmi_events_priv` stores the `wmi_device` and event type derived from WMI ID context. `lwmi_events_notify()` validates and dispatches firmware events. `lwmi_events_probe()` initializes per-device state.

## Control Flow
Probe stores the event type from the WMI ID table context. Notify handles `LWMI_EVENT_THERMAL_MODE`: it requires an ACPI integer, validates that the selected profile is one of quiet, balanced, performance, extreme, or custom, then calls the blocking notifier chain with action `LWMI_EVENT_THERMAL_MODE` and a pointer to the selected profile integer. Invalid types and unknown thermal modes are ignored or logged.

## State And Persistence
Only notifier registrations and per-WMI-device type state are maintained. The current thermal mode is not cached here; consumers such as `wmi-gamezone.c` maintain their own state after notifications.

## Dependencies And Integration Points
The driver depends on ACPI/WMI, Linux notifier chains, `wmi-events.h`, and thermal mode constants from `wmi-helpers.h`. `lenovo-wmi-gamezone` subscribes to this chain to update platform-profile state when firmware reports a mode change.

## Risks And Edge Cases
The notifier receives a pointer to a stack-local integer during notify, so subscribers must not retain the pointer. `NOTIFY_BAD` is logged but does not retry. Only thermal mode events are currently supported; new GUIDs require table and dispatch updates.

## Test Signals
Validation should inject valid and invalid thermal mode WMI integers, confirm notifier delivery and `platform_profile_notify()` behavior through subscribers, test devm unregister on consumer removal, and ensure unknown modes do not mutate consumer state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.c -->
