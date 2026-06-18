# sources/distributed-fs/ceph-client/drivers/video/backlight/cgbc_bl.c

## Purpose
This is a platform backlight driver for Congatec Board Controller managed LCD backlights. It exposes the board controller PWM duty cycle as a Linux `backlight_device` with a linear 0-100 brightness range.

## Important APIs, Types, and Functions
`struct cgbc_bl_data` stores the child device, parent `struct cgbc_device_data`, and cached `current_brightness`. `cgbc_bl_read_brightness()` issues `cgbc_command()` command `0x75` and extracts the 7-bit PWM duty field with `FIELD_GET(BLT_PWM_DUTY_MASK, ...)`. `cgbc_bl_update_status()` reads the current controller settings, preserves polarity/frequency bytes, writes a new duty cycle, and verifies the reply. `cgbc_bl_get_brightness()` refreshes hardware state before returning it.

## Control Flow
Probe fetches parent driver data from `pdev->dev.parent`, reads initial brightness, fills `backlight_properties`, and registers `cgbc-backlight` using `devm_backlight_device_register()`. Runtime updates flow from the backlight core into `update_status`; the driver avoids a write if the requested brightness matches the cached value. When a write is needed, it performs a read-modify-write transaction through CGBC firmware and only updates the cache after the controller acknowledges the new duty.

## State and Persistence
The only persistent runtime state is the in-memory cached brightness. Hardware PWM polarity and frequency are not owned by the driver; they are preserved across brightness updates by reading and replaying the existing controller reply bytes. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on `linux/backlight.h`, bitfield helpers, the CGBC MFD API in `linux/mfd/cgbc.h`, and platform-device binding name `cgbc-backlight`. It uses `BL_CORE_SUSPENDRESUME`, so suspend/resume brightness behavior is delegated through normal backlight core calls.

## Risks
The command buffer layout is firmware-contract sensitive: only byte 1 is changed on writes while reply byte 0 is interpreted as the duty field. A controller reply that reports a rounded or constrained duty value is treated as verification failure. Because updates are read-modify-write, concurrent non-driver CGBC PWM changes could be overwritten between read and write.

## Test Signals
Useful tests are probe with valid and failing `cgbc_command()`, initial brightness read, setting 0, 50, and 100, preserving non-duty PWM bits, verification mismatch returning `-EIO`, and suspend/resume update paths.
