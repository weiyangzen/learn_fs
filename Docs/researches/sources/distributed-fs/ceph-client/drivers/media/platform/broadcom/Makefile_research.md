# sources/distributed-fs/ceph-client/drivers/media/platform/broadcom/Makefile

## Purpose
This Makefile maps the Broadcom Unicam Kconfig option to its driver object.

## Important APIs, Types, and Functions
The build rule is `obj-$(CONFIG_VIDEO_BCM2835_UNICAM) += bcm2835-unicam.o`.

## Control Flow
Kbuild includes the object as built-in or module based on `CONFIG_VIDEO_BCM2835_UNICAM`.

## State and Persistence
No runtime state exists here. The file controls build output only.

## Dependencies and Integration Points
The rule must match `VIDEO_BCM2835_UNICAM` from Kconfig and the `bcm2835-unicam.c` source file.

## Risks and Edge Cases
Symbol or filename drift causes selected configurations to fail or omit the driver.

## Test Signals
Enable `CONFIG_VIDEO_BCM2835_UNICAM=m` and verify `bcm2835-unicam.ko` builds.
