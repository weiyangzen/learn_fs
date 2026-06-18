# File Research: sources/block-storage/mdadm/udev-md-raid-arrays.rules

## Purpose
udev rules for active md array devices and partitions.

## Behavior
- Filters non-md and removed devices.
- Marks arrays not ready for systemd when `array_state` is missing, clear, or inactive.
- Imports `mdadm --detail --no-devices --export`.
- Creates `/dev/disk/by-id/md-name-*`, `md-uuid-*`, and `/dev/md/*` symlinks for arrays and partitions.
- Imports blkid data and creates filesystem UUID/label/partuuid links.
- Wants `mdmonitor.service` for RAID arrays.
- Starts `mdmon@...service` for external metadata containers.
- Starts `mdadm-grow-continue@...service` for active reshape.

## Integration
Connects mdadm metadata export to udev naming and systemd service activation.
