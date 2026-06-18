# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.h

## Purpose

`hid-roccat-common.h` declares the common Roccat command/status structures, exported feature-report helper APIs, common per-device state, and macros that generate binary sysfs attributes for simple Roccat devices.

## Important APIs, Types, and Functions

- `ROCCAT_COMMON_COMMAND_CONTROL`: shared command ID for control/status operations.
- `struct roccat_common2_control`: packed control report with command, value, and request bytes.
- Exported helpers: `roccat_common2_receive`, `roccat_common2_send`, `roccat_common2_send_with_status`, `roccat_common2_device_init_struct`, `roccat_common2_sysfs_read`, and `roccat_common2_sysfs_write`.
- `struct roccat_common2_device`: common char-device claim/minor plus a mutex.
- `ROCCAT_COMMON2_SYSFS_*` and `ROCCAT_COMMON2_BIN_ATTRIBUTE_*` macros: generate typed read/write callback wrappers and static `struct bin_attribute` definitions.

## Control Flow

The macros expand in device-specific drivers to call the common sysfs helpers with fixed command IDs and fixed byte sizes. Read-only, write-only, and read/write variants set file modes `0440`, `0220`, and `0660` respectively.

## State and Persistence Behavior

`struct roccat_common2_device` is embedded or allocated per HID interface. Its mutex is the serialization point for sysfs USB transactions. The header itself has no storage.

## Dependencies and Integration Points

The header depends on USB and Linux types. It is included by most Roccat driver C files and is the shared ABI for simplified drivers that do not need device-specific cached state.

## Risks and Edge Cases

Because the macros define static symbol names such as `bin_attr_<thingy>`, they are intended for one use per translation unit per attribute name. The generated binary attributes inherit the exact-size limitations of the common helpers. Any mismatch between macro `SIZE` values and firmware report sizes causes consistent `-EIO` or rejected userspace access.

## Test Signals

Compilation across all Roccat drivers is the main contract check. Runtime tests should verify each generated bin attribute has the expected mode, size, and command behavior for a representative simple driver.
