# sources/distributed-fs/ceph-client/drivers/staging/greybus/Documentation/firmware/firmware.c

## Purpose

This user-space sample drives the Greybus firmware-management character device. It can query and update interface firmware or backend firmware using ioctl commands from `greybus_firmware.h`.

## Important APIs, Types, and Functions

Key helpers are `usage()`, `update_intf_firmware()`, and `update_backend_firmware()`. It uses ioctl structures for interface version, backend version, interface load/validate, and backend update, and sends `FW_MGMT_IOC_SET_TIMEOUT_MS`, `FW_MGMT_IOC_GET_INTF_FW`, `FW_MGMT_IOC_INTF_LOAD_AND_VALIDATE`, `FW_MGMT_IOC_MODE_SWITCH`, `FW_MGMT_IOC_GET_BACKEND_FW`, and `FW_MGMT_IOC_INTF_BACKEND_FW_UPDATE`.

## Control Flow

`main()` parses optional device, update type, firmware tag, and timeout; opens the firmware-management device; sets timeout; then dispatches to the interface or backend update path. Interface update queries current version, loads and validates a tag over UniPro, checks accepted status values, and requests mode switch. Backend update queries version, retrying while instructed, then issues backend update, again retrying on protocol retry status.

## State and Persistence Behavior

The sample itself stores only static request structs. The ioctls can cause persistent firmware changes on the module or backend and may trigger an interface mode switch.

## Dependencies and Integration Points

It depends on the Greybus firmware UAPI, POSIX file/ioctl APIs, and a kernel firmware-management device such as `/dev/gb-fw-mgmt-0`.

## Risks and Edge Cases

`strtoul()` results are not validated with `endptr`, so malformed numbers can silently parse as zero. `strncpy()` into fixed firmware-tag fields may omit NUL termination if the input is exactly the maximum size. Retry loops have no attempt limit, so a device that keeps returning retry can spin forever. Error messages do not print `errno`.

## Test Signals

Use a mock firmware-management device or fault-injection kernel path to cover interface update success/failure, backend retry success, infinite retry prevention, timeout parsing, long firmware tags, mode-switch failure, and invalid update-type arguments.
