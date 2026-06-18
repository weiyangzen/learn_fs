# sources/distributed-fs/ceph-client/drivers/hid/hid-roccat-common.c

## Purpose

`hid-roccat-common.c` provides shared USB feature-report helpers for second-generation Roccat drivers. It implements receive/send wrappers, write-status polling, common device-state initialization, and reusable sysfs binary read/write helpers.

## Important APIs, Types, and Functions

- `roccat_common2_feature_report()`: converts an 8-bit report ID to HID feature report value `0x300 | report_id`.
- `roccat_common2_receive()` and `roccat_common2_send()`: exported full-size USB control GET_REPORT/SET_REPORT wrappers.
- `roccat_common2_receive_control_status()` and `roccat_common2_send_with_status()`: poll command `ROCCAT_COMMON_COMMAND_CONTROL` until OK, busy retry, or error.
- `roccat_common2_device_init_struct()`: initializes the common device mutex.
- `roccat_common2_sysfs_read()` and `roccat_common2_sysfs_write()`: exported binary sysfs helpers for drivers using `struct roccat_common2_device`.

## Control Flow

Receive allocates a temporary kernel buffer, issues a class/interface/IN `HID_REQ_GET_REPORT` control transfer, copies exactly `size` bytes to the caller buffer, frees the temporary buffer, and returns 0 only when the transfer length equals `size`. Send duplicates caller data, issues a class/interface/OUT `HID_REQ_SET_REPORT`, frees the duplicate, and similarly requires a full-length transfer.

Status writes first send the command payload, sleep 100 ms, then call `roccat_common2_receive_control_status()`. The status loop sleeps 50 ms before each poll, treats OK as success, busy as a 500 ms retry, invalid/critical values as `-EINVAL`, and unknown values as logged `-EINVAL`.

Common sysfs helpers derive the HID and USB device from the sysfs kobject parent chain, reject partial accesses except EOF reads, serialize through `roccat_common2_device.lock`, and perform either a receive or `send_with_status`.

## State and Persistence Behavior

The file owns no global mutable state. Per-device locking and char-device state live in `struct roccat_common2_device` defined by the header and allocated by device-specific drivers. USB transfers mutate device firmware state when used for writes.

## Dependencies and Integration Points

The helpers depend on USB control messaging, HID report request constants, Linux allocation and sleep APIs, and Roccat driver sysfs parent layout. They are exported for multiple Roccat modules including KonePure, Ryos, Savu, and similar simplified drivers.

## Risks and Edge Cases

- `roccat_common2_receive()` copies `size` bytes from the temporary buffer even when the USB transfer returns a short positive length; the allocated buffer is uninitialized beyond `len`.
- The status polling loop can run forever if firmware continuously reports busy.
- The sysfs helpers assume the kobject parent chain maps to a USB interface and common device state.
- Exact-size sysfs access is simple but unfriendly to partial reads used by some tooling.

## Test Signals

Test full, short, and negative USB control transfers; busy-to-OK and busy-forever control polling; invalid/critical status handling; exact-size sysfs read/write rejection; and concurrent sysfs access serialization through the common mutex.
