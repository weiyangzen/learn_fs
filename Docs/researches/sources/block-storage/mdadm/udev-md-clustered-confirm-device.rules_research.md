# File Research: sources/block-storage/mdadm/udev-md-clustered-confirm-device.rules

## Purpose
udev rules for clustered md device confirmation.

## Behavior
- Applies only to block md disk change events with `EVENT=ADD_DEVICE`, `DEVICE_UUID`, and `RAID_DISK`.
- Uses `blkid -o device -t UUID_SUB=...` to find the new component.
- Runs `mdadm --manage <array> --cluster-confirm <raid_disk>:<device|missing>`.

## Integration
Supports clustered md membership confirmation when a node is asked to confirm a device by UUID.
