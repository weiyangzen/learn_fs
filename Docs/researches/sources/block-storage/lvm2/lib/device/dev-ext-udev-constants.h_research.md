# File Research: sources/block-storage/lvm2/lib/device/dev-ext-udev-constants.h

## Purpose
Defines udev property and sysfs attribute names used by LVM2's external device information layer.

## Constants
The header names udev properties for filesystem type, multipath component markers, firmware/software RAID detection, partition table type, device type, device symlinks, and multipath path status. It also defines the sysfs `size` attribute name.

## Integration
Included by udev-backed probing code in MD, multipath, and external device-handle modules.

## Risk Notes
These string constants encode contracts with udev rules, blkid, and multipath. If distribution udev properties change, detection behavior can diverge from native sysfs/signature probing.
