# sources/distributed-fs/ceph-client/include/uapi/linux/misc/bcm_vk.h

## Purpose
Defines Broadcom Valkyrie misc device ioctls and firmware status register bit encodings for firmware loading, reset, readiness, deinit, and reset reason reporting.

## Important APIs, Types, And Functions
Exports `vk_image`, `vk_reset`, `VK_IOCTL_LOAD_IMAGE`, `VK_IOCTL_RESET`, image types `VK_IMAGE_TYPE_BOOT1/BOOT2`, firmware status BAR offsets, readiness/deinit masks, and reset reason fields.

## Control Flow
Userspace passes a firmware image descriptor or reset arguments through ioctls. Firmware status is read from BAR offsets and decoded through bit masks to determine boot phases, app readiness, deinit progress, reset completion, and reset cause.

## State, Persistence, And Dependencies
Persistent state is in device firmware and BAR registers. The header depends on `linux/ioctl.h` and `linux/types.h`.

## Integration Points
Used by the BCM VK kernel driver and device-management utilities that stage boot images and monitor firmware lifecycle.

## Risks
The filename is a fixed 64-byte array and must be terminated/validated by userspace and driver. Firmware state bits may be transient, and reset reason decoding depends on top-nibble masking.

## Test Signals
Verify ioctl numbers, image type validation, filename bounds, reset argument handling, BAR status decode, ready/deinit masks, and reset reason extraction.
