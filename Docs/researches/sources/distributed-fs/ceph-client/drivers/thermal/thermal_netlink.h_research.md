# sources/distributed-fs/ceph-client/drivers/thermal/thermal_netlink.h

## Purpose
`thermal_netlink.h` is the internal declaration and stub layer for thermal generic-netlink notifications and control.

## Important APIs, Types, and Functions
It defines `struct thermal_genl_cpu_caps`, multicast group enum values, notifier action constants, `struct thermal_genl_notify`, and all notification/init/notifier prototypes. Disabled builds return zero for every notification/control helper and no-op exit.

## Control Flow
The header has no runtime flow. It allows thermal core code to issue netlink notifications and sampling messages without config-specific branches.

## State and Persistence Behavior
No state is stored here. Enabled builds use `thermal_netlink.c` to maintain the netlink family and listener notifier chain; disabled builds drop all events.

## Dependencies and Integration Points
It forward-declares thermal zone, trip, and cooling-device types, and is included by the thermal core, helpers, and threshold code.

## Risks and Edge Cases
Because disabled stubs return success, callers cannot treat a zero return as proof that userspace saw an event. API drift between stubs and implementation is the key build risk.

## Test Signals
Compile with `CONFIG_THERMAL_NETLINK=y` and unset; verify all call sites build; in enabled builds, pair with netlink event/command tests.
