# sources/distributed-fs/ceph-client/include/linux/firmware.h

## Purpose

`sources/distributed-fs/ceph-client/include/linux/firmware.h` declares the kernel firmware loader API and firmware upload interface. The source was read as a complete 216-line file for this report.

## Important APIs, Types, and Functions

Key definitions include `FW_ACTION_NOUEVENT`, `FW_ACTION_UEVENT`, `struct firmware`, `enum fw_upload_err`, `struct fw_upload`, `struct fw_upload_ops`, `firmware_request_builtin`, `request_firmware`, `firmware_request_nowait_nowarn`, `firmware_request_nowarn`, `firmware_request_platform`, `request_firmware_nowait`, `request_firmware_direct`, `request_firmware_into_buf`, `request_partial_firmware_into_buf`, `release_firmware`, `firmware_upload_register`, `firmware_upload_unregister`, `firmware_request_cache`, and cleanup helper `DEFINE_FREE(firmware, ...)`.

## Control Flow

Drivers request firmware synchronously, asynchronously, directly, from platform fallback, into provided buffers, or by partial reads. Successful requests return a `struct firmware` that must be released. Firmware upload users register device-specific prepare/write/poll/cancel/cleanup ops; the firmware loader calls them to push update data to hardware and report upload errors.

## State and Persistence Behavior

`struct firmware` carries size/data plus private loader state. Upload state is in `struct fw_upload` and driver-private handles. Firmware data is transient kernel memory; actual persistent update effects are device-specific flash or secure storage.

## Dependencies and Integration Points

It depends on kernel types, compiler attributes, cleanup helpers, and GFP flags. It integrates with the firmware loader, module/device model, sysfs fallback/uevent policy, built-in firmware, platform firmware, and device firmware update flows.

## Risks and Edge Cases

Availability depends on `CONFIG_FW_LOADER` reachability; disabled stubs return `-EINVAL`. Async callbacks must handle lifetime of context and firmware. Upload cancel runs from a different kernel thread, so driver ops must be race-safe. Buffer and partial requests require size/offset validation.

## Test Signals

Firmware loader selftests, built-in/direct/nowait/platform request tests, missing firmware error paths, release/cleanup-class tests, firmware upload sysfs tests, cancellation/race tests, and disabled-config build tests.
