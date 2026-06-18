# File Research: sources/block-storage/mdadm/udev.h

## Purpose
Header for mdadm udev helpers.

## Contents
- Defines `enum udev_status` with no-udev, error, success, and timeout values.
- Declares `udev_is_available()`.
- Declares `udev_wait_for_events()` when libudev support is enabled.
- Declares `udev_block()` and `udev_unblock()`.

## Integration
Included by `udev.c` and consumers that need to block or wait for udev behavior.
