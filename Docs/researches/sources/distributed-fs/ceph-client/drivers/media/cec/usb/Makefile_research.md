# sources/distributed-fs/ceph-client/drivers/media/cec/usb/Makefile

## Purpose
This Makefile builds USB/serial CEC adapter subdirectories.

## Important APIs, Types, and Functions
It maps `CONFIG_USB_EXTRON_DA_HD_4K_PLUS_CEC`, `CONFIG_USB_PULSE8_CEC`, and `CONFIG_USB_RAINSHADOW_CEC` to their respective subdirectories.

## Control Flow
Kbuild descends into selected driver directories and builds their local composite objects.

## State and Persistence
No runtime state is present.

## Dependencies and Integration Points
It connects top-level CEC USB build selection to the Extron, Pulse8, and RainShadow driver implementations.

## Risks and Test Signals
Build tests should confirm each subdirectory is included only under its matching config.
