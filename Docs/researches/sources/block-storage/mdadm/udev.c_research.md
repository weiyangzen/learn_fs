# File Research: sources/block-storage/mdadm/udev.c

## Purpose
Provides mdadm helpers for detecting udev, optionally waiting for udev block events, and blocking/unblocking udev handling while arrays are being created.

## Main Responsibilities
- `udev_is_available()` checks `/dev/.udev` or `/run/udev` and honors `MDADM_NO_UDEV`.
- When libudev is enabled, initializes a block-device udev monitor and waits for events with timeout.
- `udev_block()` creates `/run/mdadm/creating-<devnm>`.
- `udev_unblock()` removes the saved blocking file.

## Integration
Works with `udev-md-raid-creating.rules`, which marks matching md devices as not systemd-ready while the block file exists.

## Risks and Edge Cases
- `udev_block()` stores one global unblock path, so overlapping create operations in one process would need careful sequencing.
- The libudev monitor is process-global and released through `atexit()`.
