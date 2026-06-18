# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.h

## Purpose
Declares sysfs registration helpers for b43legacy wireless devices.

## Important APIs, Types, and Functions
Forward declares `struct b43legacy_wldev` and exposes `b43legacy_sysfs_register()` and `b43legacy_sysfs_unregister()`.

## Control Flow, State, and Persistence
No state in the header. Attribute lifetime is controlled by `sysfs.c` and the device lifecycle.

## Dependencies and Integration Points
Included by b43legacy setup/teardown code and by `sysfs.c`.

## Risks and Test Signals
Risks are prototype drift and lifecycle mismatch. Build and module load/unload with sysfs attribute presence/absence are sufficient signals.
