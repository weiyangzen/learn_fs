# sources/distributed-fs/ceph-client/drivers/media/cec/usb/rainshadow/Kconfig

## Purpose
This Kconfig entry enables the RainShadow Tech HDMI CEC USB/serial adapter driver.

## Important APIs, Types, and Functions
It defines `USB_RAINSHADOW_CEC` as a tristate and selects `CEC_CORE`, `USB`, `USB_ACM`, `SERIO`, and `SERIO_SERPORT`.

## Control Flow
When enabled, the module name is `rainshadow-cec`.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
The selections match a USB ACM device exposed through serio and integrated with the CEC core.

## Risks and Test Signals
Configuration tests should verify availability only with USB/serio dependencies and correct module naming.
