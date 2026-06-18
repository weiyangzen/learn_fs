# File Research: sources/block-storage/mdadm/udev-md-raid-safe-timeouts.rules

## Purpose
udev rule set that attempts to set safer drive timeouts for disks containing RAID members.

## Behavior
- Skips anaconda contexts and command-line-disabled dmraid/mdadm handling.
- Applies to partition devices with exported mdadm metadata.
- For RAID levels above 0, checks parent disk timeout sysfs file and `smartctl` SCTERC output.
- If SCTERC does not appear enabled, writes `180` to `/sys/block/$parent/device/timeout` and logs the change.

## Integration
Independent safety-oriented udev helper for disks used in mdraid.
