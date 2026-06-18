# sources/distributed-fs/ceph-client/include/uapi/linux/thermal.h

## Purpose
Defines thermal subsystem UAPI names, modes, trip types, generic netlink family metadata, attributes, events, sampling groups, and commands.

## Important APIs, Types, and Constants
Constants include `THERMAL_NAME_LENGTH`, threshold direction bits, family name `thermal`, version `0x02`, and multicast group names. Enums define device mode disabled/enabled and trip types active/passive/hot/critical. Generic netlink attributes cover thermal zones, trip IDs/types/temps/hysteresis, modes, names, cooling devices, governors, CPU capability, thresholds, previous temperature, and weights. Events cover zone create/delete/enable/disable, trip crossing/change/add/delete, cooling device add/delete/state update, governor change, CPU capability change, and threshold add/delete/flush/up/down. Commands query zone IDs, trips, temperatures, governors, modes, cooling devices, thresholds, and mutate thresholds.

## Control Flow, State, and Persistence
Userspace sends generic netlink commands to query or modify thermal threshold state and subscribes to event/sampling groups. Kernel maintains thermal zone, trip, cooling device, governor, and threshold state.

## Dependencies and Integration Points
No explicit includes. Integrates with thermal core, generic netlink, platform thermal drivers, and power/monitoring daemons.

## Risks and Test Signals
Risks include threshold direction confusion, event versioning, policy daemons relying on names, and missing attributes in older kernels. Test netlink family discovery, every query command, threshold add/delete/flush, event multicast delivery, and unknown attribute tolerance.
