# sources/distributed-fs/ceph-client/drivers/media/cec/usb/extron-da-hd-4k-plus/Kconfig

## Purpose
This Kconfig entry enables the Extron DA HD 4K Plus HDMI splitter CEC driver.

## Important APIs, Types, and Functions
It defines `USB_EXTRON_DA_HD_4K_PLUS_CEC` as a tristate. It depends on `VIDEO_DEV`, `USB`, and `USB_ACM`, and selects `CEC_CORE`, `SERIO`, and `SERIO_SERPORT`.

## Control Flow
When enabled, the module name is `extron-da-hd-4k-plus-cec`.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The dependencies reflect that the implementation exposes V4L2 video devices and CEC adapters over a USB ACM serial line represented as a serio port.

## Risks and Test Signals
Configuration tests should verify V4L2 and USB ACM prerequisites. Since the driver uses V4L2 EDID ioctls, missing `VIDEO_DEV` would break the implementation.
