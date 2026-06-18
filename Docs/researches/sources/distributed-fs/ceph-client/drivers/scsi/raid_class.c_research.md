# sources/distributed-fs/ceph-client/drivers/scsi/raid_class.c

## Purpose
`raid_class.c` implements a generic RAID visualization transport class. It lets RAID-capable lower-level drivers expose RAID attributes through a common sysfs transport container independent of the specific hardware or software RAID implementation.

## Important APIs, Types, And Functions
`struct raid_internal` wraps public `struct raid_template`, the provider's `raid_function_template`, and three attributes. `struct raid_component` represents component devices linked under `raid_data`. The public exports are `raid_class_attach()` and `raid_class_release()`. Matching/setup/removal is handled by `raid_match()`, `raid_setup()`, and `raid_remove()`. Attribute helpers map enum values through `raid_state_name()` and `raid_level_name()`, and generated sysfs show methods expose `level`, `resync`, and `state`.

## Control Flow
Module init registers the `raid_class` transport class. A RAID provider calls `raid_class_attach()` with callbacks and a cookie; this allocates internal state, sets the attribute-container class/match/attrs fields, registers the container, and publishes the three attributes. When transport matching sees a SCSI device, `raid_match()` verifies the provider cookie matches the SCSI host template and calls `is_raid()`. `raid_setup()` allocates `struct raid_data` and initializes its component list. `raid_remove()` unregisters all component devices, detaches driver data, and frees the RAID data. Release unregisters the attribute container and frees `raid_internal`.

## State And Persistence
State is in memory only. Per-template state records provider callbacks and sysfs attributes. Per-class-device state is `struct raid_data`, including level/state/resync values and a component list managed by other RAID code. The class does not persist RAID configuration; it reflects state supplied by the provider callbacks and device data.

## Dependencies And Integration Points
The file depends on Linux transport class/attribute container infrastructure, sysfs device attributes, list handling, allocation, and SCSI device/host helpers. Its primary integration point is `include/linux/raid_class.h` providers that supply `cookie`, `is_raid()`, and optional `get_resync()`/`get_state()` callbacks.

## Risks And Edge Cases
`raid_remove()` logs removal at error severity, which can be noisy for normal teardown. Attribute show helpers assume `dev_get_drvdata()` returns a valid `raid_data`. `raid_state_name()` and `raid_level_name()` return `NULL` for unknown enum values not in the tables, which could feed a `%s` sysfs print. The matching path currently only handles SCSI devices and explicitly leaves other subsystems as a FIXME. `BUG_ON()` is used for unexpected registration/unregistration and attribute-count failures.

## Test Signals
Signals include successful class registration/unregistration, provider attach/release, SCSI RAID device matching by cookie and `is_raid()`, sysfs `level`, `resync`, and `state` reads with and without provider update callbacks, component list cleanup on device removal, and behavior for unknown RAID level/state enum values.
