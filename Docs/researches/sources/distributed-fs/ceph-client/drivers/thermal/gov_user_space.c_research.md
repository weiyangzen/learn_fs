# sources/distributed-fs/ceph-client/drivers/thermal/gov_user_space.c

## Purpose
Thermal governor that notifies userspace about trip crossings via uevents rather than applying cooling policy itself.

## Important APIs, Types, and Functions
- `user_space_bind()` emits a one-time info message recommending thermal netlink.
- `user_space_trip_crossed()` creates `NAME`, `TEMP`, `TRIP`, and `EVENT` environment variables and sends `KOBJ_CHANGE`.
- Declares `thermal_gov_user_space`.

## Control Flow
On bind, the governor logs once. On every trip crossing under the zone lock, it allocates four strings, sends a kobject uevent on the thermal-zone device, and frees the strings.

## State and Persistence
No governor-private state. It uses current thermal-zone fields at event time.

## Dependencies and Integration Points
Integrates with thermal core trip-crossing notifications, kobject uevents, sysfs device model, and userspace listeners.

## Risks and Edge Cases
- `kasprintf()` failures are not checked before passing the environment array to `kobject_uevent_env()`.
- It does not throttle; system safety depends on firmware, critical trips, or userspace policy responsiveness.
- Uevents can be lossy under userspace pressure.

## Test Signals
Tests should verify uevent environment contents, trip id mapping, upward/downward crossing delivery, bind log behavior, and allocation-failure robustness if fault injection is available.
