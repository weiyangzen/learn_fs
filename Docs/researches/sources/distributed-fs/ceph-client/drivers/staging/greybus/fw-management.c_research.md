# sources/distributed-fs/ceph-client/drivers/staging/greybus/fw-management.c

## Purpose
Firmware management protocol driver. It exposes a character-device ioctl API for userspace to query interface/backend firmware versions, load and validate interface firmware, update backend firmware, set operation timeout, and request interface mode switch.

## Important APIs, Types, And Functions
`struct fw_mgmt` holds the management connection, kref/list entry, request ID allocator, ioctl mutex, completion, char device, timeout, disabled/mode-switch flags, and pending/result fields for interface and backend firmware operations. Main operations include `fw_mgmt_interface_fw_version_operation()`, `fw_mgmt_load_and_validate_operation()`, `fw_mgmt_backend_fw_version_operation()`, and `fw_mgmt_backend_fw_update_operation()`. Unsolicited completions are handled by `fw_mgmt_interface_fw_loaded_operation()` and `fw_mgmt_backend_fw_updated_operation()`.

## Control Flow
Connection init allocates `fw_mgmt`, adds it to a global list, enables the Greybus connection, allocates a minor, registers a cdev, and creates a class device. Open finds the object by cdev under `list_mutex` and takes a kref. Ioctls are serialized by `fw_mgmt->mutex`, protected by runtime PM, and reject new operations when disabled or after mode switch starts. Load/update operations allocate request IDs, send Greybus commands, wait for completion, and copy results to userspace.

## State And Persistence
State is per management connection and lifetime-managed by kref. Pending request IDs and result fields persist across the request/completion wait. `mode_switch_started` permanently blocks further ioctls until disconnect. No on-disk state is written.

## Dependencies And Integration Points
Uses Greybus firmware management protocol messages, Linux cdev/class APIs, ioctl copy helpers, completions, IDA, krefs, runtime PM, and the user ABI in `greybus_firmware.h`. Mode switching calls `gb_interface_request_mode_switch()`.

## Risks
Completion reuse requires serialized ioctls; parallel operations would corrupt result fields. On timeout, request IDs are not explicitly reclaimed in this function, so subsequent completions and ID allocator behavior are sensitive areas. Disconnect must block new users, wait out active ioctls, disable the connection, and drop krefs in order.

## Test Signals
Cover every ioctl, invalid load methods, oversized/truncated firmware tags, timeout changes including zero rejection, unsolicited completion with wrong/no request ID, disconnect with open file descriptors, mode switch success/failure, and runtime-PM get failures.
