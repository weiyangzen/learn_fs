# sources/distributed-fs/ceph-client/drivers/staging/greybus/greybus_firmware.h

## Purpose
User ABI header for Greybus firmware management ioctls. It defines userspace-visible firmware tag size, load methods, status codes, version status codes, packed ioctl payloads, and ioctl command numbers.

## Important APIs, Types, And Functions
Defines `GB_FIRMWARE_U_TAG_MAX_SIZE`, public load method constants, interface load status constants, backend firmware update status constants, and backend version status constants. Payload structs are `fw_mgmt_ioc_get_intf_version`, `fw_mgmt_ioc_get_backend_version`, `fw_mgmt_ioc_intf_load_and_validate`, and `fw_mgmt_ioc_backend_fw_update`. Ioctls include get interface firmware, get backend firmware, interface load/validate, backend update, set timeout, and mode switch.

## Control Flow
No executable flow. `fw-management.c` consumes these ioctl structs in its character-device unlocked ioctl path and maps them to Greybus management operations.

## State And Persistence
No runtime state. The packed struct layout is a persistent kernel/userspace ABI and must remain stable.

## Dependencies And Integration Points
Includes Linux ioctl and fixed-width type headers. It integrates directly with the `gb_fw_mgmt` class device created by firmware management connection init.

## Risks
Tag size is only 10 bytes and operations use padded copies; truncation must be rejected by implementation. ABI constants mirror Greybus protocol statuses but are user-facing, so renumbering is not safe.

## Test Signals
Check ioctl numbers and struct sizes, timeout ioctl with zero and nonzero values, tag truncation behavior, mode switch gating, backend status propagation, and compatibility builds.
