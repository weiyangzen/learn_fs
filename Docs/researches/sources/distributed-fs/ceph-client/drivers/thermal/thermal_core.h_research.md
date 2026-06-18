# sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/thermal/thermal_core.h` is the private thermal subsystem header shared across core, sysfs, governors, debugfs, thresholds, and helper modules. It defines the internal thermal-zone, trip, governor, and instance structures that back the public thermal APIs. The source was read as a complete 309-line file.

## Important APIs, Types, and Functions

Key types are `struct thermal_attr`, `struct thermal_trip_attrs`, `struct thermal_trip_desc`, `struct thermal_governor`, `struct thermal_zone_device`, and `struct thermal_instance`. It defines state flags `TZ_STATE_FLAG_SUSPENDED`, `TZ_STATE_FLAG_RESUMING`, `TZ_STATE_FLAG_INIT`, `TZ_STATE_FLAG_EXIT`, the `THERMAL_NO_TARGET` sentinel, default governor selection macros, governor linker-table macros, iteration helpers, guards for zone locking, `trip_to_trip_desc()`, and prototypes for thermal core/sysfs/helper functions.

## Control Flow

The header contributes no executable flow by itself. It shapes how `thermal_core.c` moves trips among lists, how governors are declared and discovered, how sysfs/debugfs access shared state, and how cooling devices bind to trips.

## State and Persistence Behavior

It defines in-memory runtime state layout. `struct thermal_zone_device` contains device identity, completions, trip lists, temperatures, delays, ops, governor data, locks, poll work, state flags, optional debugfs state, user thresholds, and a flexible array of trip descriptors. `struct thermal_instance` describes one cdev-to-trip binding.

## Dependencies and Integration Points

It includes public `linux/thermal.h`, cleanup guards, device APIs, thermal netlink, thresholds, and debugfs headers. It is intentionally private: platform drivers normally include `linux/thermal.h`, while subsystem internals and `soctherm.c` use this header for helper access.

## Risks and Edge Cases

Structure changes can affect many thermal subsystem files. Lock guard semantics are embedded here; misuse can deadlock or unlock incorrectly. The default governor macro depends on exactly one Kconfig default. Flexible array and `__counted_by(num_trips)` require registration allocation to stay aligned. Trip descriptor list membership must stay consistent with `threshold`.

## Test Signals

Compile coverage for all thermal governors, sysfs, debugfs, thresholds, and platform drivers catches many issues. Runtime registration/unregistration and lockdep tests are important after changing structures or guard definitions.
