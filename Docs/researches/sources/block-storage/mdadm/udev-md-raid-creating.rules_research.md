# File Research: sources/block-storage/mdadm/udev-md-raid-creating.rules

## Purpose
udev guard rule for arrays currently being created by mdadm.

## Behavior
- If `/run/mdadm/creating-$kernel` exists for an `md*` device, sets `SYSTEMD_READY=0`.

## Integration
Pairs with `udev_block()`/`udev_unblock()` in `udev.c` to stop udev/systemd from treating a newly created array as ready too early.
