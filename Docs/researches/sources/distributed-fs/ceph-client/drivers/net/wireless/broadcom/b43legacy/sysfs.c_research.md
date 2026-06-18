# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/sysfs.c

## Purpose
Provides legacy b43 sysfs attributes for privileged runtime tuning of interference mitigation and short preamble mode.

## Important APIs, Types, and Functions
Helpers `get_integer()` and `get_boolean()` parse sysfs input. Attribute handlers implement `interference` show/store and `shortpreamble` show/store. `b43legacy_sysfs_register()` creates `interference` and `shortpreamble`; `b43legacy_sysfs_unregister()` removes them.

## Control Flow, State, and Persistence
All show/store operations require `CAP_NET_ADMIN`. Interference writes parse modes 0-3, lock `wl->mutex` and `wl->irq_lock`, call `b43legacy_radio_set_interference_mitigation()`, and store the resulting mode in PHY state via radio code. Short-preamble writes parse common boolean strings and update `wldev->short_preamble` under the same locks. State lasts for the active device instance and is not persisted to disk.

## Dependencies and Integration Points
Depends on Linux device sysfs, capability checks, b43legacy device conversion helpers, radio interference mitigation, and PHY constants. It is registered after the device reaches `B43legacy_STAT_INITIALIZED`.

## Risks and Test Signals
Risks include accepting malformed input, changing radio registers while interrupts race, exposing knobs without permission, and failing cleanup if the second file creation fails. Test with root/non-root reads and writes, all interference modes, invalid values, module removal, and radio behavior after manual WLAN/non-WLAN mitigation.
