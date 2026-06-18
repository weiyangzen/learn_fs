# sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.c

## Purpose
`thermal_netlink.c` implements the thermal framework's generic-netlink family for event multicast, sampling multicast, and request/reply commands exposing zones, trips, governors, cooling devices, CPU capabilities, and user thresholds.

## Important APIs, Types, and Functions
Important state includes `thermal_genl_family`, `thermal_genl_policy`, multicast groups, `struct param`, `event_cb`, `cmd_cb`, and `thermal_genl_chain`. Public APIs include `thermal_notify_tz_*`, `thermal_notify_cdev_*`, `thermal_notify_threshold_*`, `thermal_genl_sampling_temp`, `thermal_genl_cpu_capability_event`, notifier register/unregister, and init/exit.

## Control Flow
Sampling sends a `THERMAL_GENL_SAMPLING_TEMP` multicast only if listeners exist. Event helpers fill `struct param` and call `thermal_genl_send_event`, which allocates a skb, emits a generic-netlink header, runs the event encoder, ends the message, and multicasts to the event group. Command paths allocate reply messages for `doit` or write into dump skbs for `dumpit`, dispatch through `cmd_cb`, and encode nested zone/cdev/trip/threshold data. Threshold mutation commands require `CAP_SYS_ADMIN` and hold the target zone lock before changing the threshold list.

## State and Persistence Behavior
The netlink family is registered at thermal init and unregistered at exit. Listener bind/unbind is broadcast through a blocking notifier chain. The module does not persist data itself; it snapshots live thermal core state and mutates only user threshold lists via thermal threshold helpers.

## Dependencies and Integration Points
It depends on `<uapi/linux/thermal.h>`, generic netlink, capability checks, notifier chains, thermal zone/cdev iterators, `thermal_zone_get_temp`, `thermal_zone_trip_id`, and `thermal_thresholds_*`. It is the userspace ABI counterpart to sysfs and tracepoints.

## Risks and Edge Cases
Many commands use relaxed validation flags, so policy coverage and explicit attribute checks are important. Encoders return `-EMSGSIZE` on nested attribute failure; missing `nla_nest_cancel` on some command error paths is a common audit point. Event array indexing assumes valid enum values from internal callers.

## Test Signals
Generic-netlink family registration tests, listener/no-listener multicast behavior, `genl` dump/get commands for zones and cdevs, capability enforcement for threshold add/delete/flush, malformed attribute tests, and crossing thresholds to observe up/down events.
