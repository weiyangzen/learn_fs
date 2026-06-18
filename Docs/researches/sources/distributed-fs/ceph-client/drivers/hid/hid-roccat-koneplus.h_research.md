# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-koneplus.h

## Purpose

`hid-roccat-koneplus.h` defines Kone[+]/XTD report sizes, command IDs, profile-selection control request IDs, info/profile report layouts, button interrupt report format, userspace event payload, and per-device state.

## Important APIs, Types, and Functions

- `KONEPLUS_SIZE_*`: binary sysfs and firmware payload sizes.
- `enum koneplus_control_requests`: profile settings and buttons selection requests.
- `struct koneplus_actual_profile` and `struct koneplus_info`: small feature-report payloads.
- `enum koneplus_commands`: feature command IDs, including shared `0x0c` for TCU and TCU image.
- `struct koneplus_mouse_report_button` and button type/action enums: report 3 event contract.
- `struct koneplus_roccat_report` and `struct koneplus_device`: userspace event and cached state.

## Control Flow

The C file uses the size and command constants to generate sysfs accessors. Button reports are cast according to this header and converted to char-device events.

## State and Persistence Behavior

Only the active zero-based profile is cached in `struct koneplus_device`. Profile data, buttons, macros, sensor, TCU, and talk settings live in firmware and are accessed through fixed-size reports.

## Dependencies and Integration Points

This header is coupled to `hid-roccat-common.h` generated attributes, KonePlus firmware protocol, and userspace Roccat tooling that consumes the binary sysfs files.

## Risks and Edge Cases

Command `KONEPLUS_COMMAND_TCU` and `KONEPLUS_COMMAND_TCU_IMAGE` both use `0x0c`; the driver distinguishes read/write by payload size and attribute. Changing sizes or packed fields breaks userspace and firmware protocol.

## Test Signals

Verify binary attribute sizes, profile report range 0-4, button report parsing for all type enums, and the shared TCU command behavior.
