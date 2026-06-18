<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-camera.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-camera.c

## Purpose
This Lenovo WMI camera button driver converts a Lenovo camera shutter WMI event into the Linux input switch `SW_CAMERA_LENS_COVER`. It targets the event GUID `50C76F1F-D8E4-D895-0A3D-62F4EA400013` and reports whether the physical privacy shutter is open or closed.

## Important APIs, Types, And Functions
The private state is `struct lenovo_wmi_priv`, holding an `input_dev` pointer and a `notify_lock` mutex. `camera_shutter_input_setup()` allocates and registers the input device, sets `EV_SW/SW_CAMERA_LENS_COVER`, and seeds the switch state from the first WMI event. `lenovo_wmi_notify()` validates the ACPI event object, lazily creates the input device, and reports switch changes. `lenovo_wmi_probe()` allocates state and initializes the mutex; `lenovo_wmi_remove()` unregisters the input device and destroys the mutex. The module is registered as a `wmi_driver` with `min_event_size = sizeof(u8)` and `no_singleton = true`.

## Control Flow
Probe only allocates state; the input device is not registered until a valid event arrives. Notify accepts only one-byte ACPI buffers: `0` means camera closed, `1` means camera open. The driver reports Linux switch value `1` for lens covered and `0` for uncovered, so it inverts the firmware's open/closed value when needed. Invalid object types, buffer lengths, and mode values are rejected with device log messages.

## State And Persistence
State is runtime-only: an input device pointer plus a mutex. No firmware value is persisted by the driver. The initial userspace-visible switch state is whichever valid camera mode is delivered by the first event.

## Dependencies And Integration Points
The driver depends on ACPI/WMI, input core, and Lenovo firmware event semantics. Userspace consumes the switch through evdev/libinput-style input interfaces. `PROBE_PREFER_ASYNCHRONOUS` and `no_singleton` allow multiple WMI instances without blocking boot.

## Risks And Edge Cases
Because the input device is lazily created, systems that never emit an initial event will not expose the switch. Firmware returning unexpected buffer encodings is ignored. The notify mutex serializes lazy registration and reporting, but there is no cached last value outside the input core.

## Test Signals
Useful checks include WMI event injection with mode `0` and `1`, validation that `/dev/input` reports `SW_CAMERA_LENS_COVER` with inverted semantics, malformed-event tests for non-buffer and wrong-length objects, module remove after lazy registration, and multi-instance WMI enumeration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/lenovo/wmi-camera.c -->
