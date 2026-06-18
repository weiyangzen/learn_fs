# sources/distributed-fs/ceph-client/drivers/media/cec/usb/Kconfig

## Purpose
This Kconfig file groups USB/serial CEC adapter drivers.

## Important APIs, Types, and Functions
It does not define code APIs. Under `USB_SUPPORT && TTY`, it sources Kconfig files for Extron DA HD 4K Plus, Pulse Eight, and RainShadow drivers.

## Control Flow
Menu inclusion is conditional on USB and TTY support because these drivers bind through USB ACM/serio serial transport.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
It integrates child Kconfig menus with the media CEC build. Child drivers select `CEC_CORE`, USB, USB ACM, SERIO, and SERPORT as needed.

## Risks and Test Signals
Configuration tests should confirm child entries are hidden when TTY or USB support is unavailable and visible when prerequisites are enabled.
