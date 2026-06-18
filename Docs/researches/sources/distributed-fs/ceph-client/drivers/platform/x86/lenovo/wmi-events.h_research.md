<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.h -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.h

## Purpose
This header exposes the Lenovo WMI event notifier API. It defines event type identifiers and lets Lenovo platform drivers subscribe to events without binding directly to WMI GUID handlers.

## Important APIs, Types, And Functions
`enum lwmi_events_type` currently defines `LWMI_EVENT_THERMAL_MODE = 1`. The exported functions are `lwmi_events_register_notifier()`, `lwmi_events_unregister_notifier()`, and `devm_lwmi_events_register_notifier()`. Forward declarations keep the header lightweight.

## Control Flow
There is no direct runtime control flow. Consumers create a `notifier_block`, assign `notifier_call`, and register it. The implementation in `wmi-events.c` later invokes subscribers through a blocking notifier chain when firmware events arrive.

## State And Persistence
The header owns no state. Notifier state is stored by the implementation and by each consumer's `notifier_block`.

## Dependencies And Integration Points
The interface integrates `wmi-events.c` with consumers such as `wmi-gamezone.c`. It uses standard Linux notifier semantics and is exported under the Lenovo WMI events namespace.

## Risks And Edge Cases
Consumers must handle the data pointer as event-specific and transient. Adding new event types requires keeping enum values and implementation dispatch synchronized.

## Test Signals
Build tests should verify namespace imports and prototypes. Runtime tests should register and unregister a dummy notifier and confirm only expected action IDs reach it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-events.h -->
