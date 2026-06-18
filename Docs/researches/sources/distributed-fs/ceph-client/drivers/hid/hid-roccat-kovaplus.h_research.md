# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-kovaplus.h

## Purpose

`hid-roccat-kovaplus.h` defines Kova[+] report sizes, control requests, packed profile/info/actual-profile payloads, mouse button report types, Roccat event payload, and cached device state.

## Important APIs, Types, and Functions

- `KOVAPLUS_SIZE_*`: fixed payload sizes for control, info, profile settings, and profile buttons.
- `enum kovaplus_control_requests`: profile settings/buttons selectors.
- `struct kovaplus_actual_profile`, `struct kovaplus_profile_settings`, `struct kovaplus_profile_buttons`, and `struct kovaplus_info`.
- `enum kovaplus_mouse_report_button_types`: profile, macro, shortcut, quicklaunch, timer, CPI, sensitivity, and multimedia event types.
- `struct kovaplus_roccat_report` and `struct kovaplus_device`.

## Control Flow

The C file uses control request IDs to choose which profile data subsequent reads return. Mouse report type constants drive cache updates and char-device event construction.

## State and Persistence Behavior

Profile settings/buttons are cached in `struct kovaplus_device`, along with active profile/CPI/sensitivity. The packed profile structures represent firmware state and are surfaced to userspace.

## Dependencies and Integration Points

The header depends on Linux fixed-width types and is consumed by the Kova[+] driver and Roccat userspace tools via the binary sysfs ABI.

## Risks and Edge Cases

Several type comments describe one-based firmware values while cached profile indices are zero-based. Layout or enum changes would break both firmware interaction and event decoding.

## Test Signals

Size/layout checks, profile index conversion tests, CPI event conversion, and event-type coverage should guard this header contract.
