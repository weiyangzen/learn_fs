# sources/distributed-fs/ceph-client/drivers/mmc/core/bus.h

## Purpose
Private declarations for the MMC bus and MMC media-driver interface.

## Important APIs, Types, And Functions
- `MMC_DEV_ATTR()` helper for read-only card sysfs attributes.
- `struct mmc_driver` wraps a `device_driver` plus card `probe`, `remove`, and `shutdown`.
- Declares card allocation/add/remove, bus register/unregister, and driver register/unregister helpers.

## Control Flow
Protocol code registers cards; media drivers register `struct mmc_driver`; `bus.c` bridges those callbacks to the driver core.

## State And Persistence
No header-owned state. Contracts create card/driver state in the runtime driver model.

## Dependencies And Integration Points
Depends on device/sysfs headers and internal MMC host/card users.

## Risks And Edge Cases
Changing callback shapes requires synchronized updates across MMC media drivers.

## Test Signals
Compile all MMC media drivers and runtime probe/remove of `mmcblk`.
