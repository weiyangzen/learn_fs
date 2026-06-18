# sources/distributed-fs/ceph-client/net/openvswitch/meter.h

## Purpose
`meter.h` declares Open vSwitch datapath meter structures and public functions. It is included by datapath and action code to initialize meter tables and execute meter actions.

## Important APIs and Types
Constants define current limits: `DP_MAX_BANDS` is one, `DP_METER_ARRAY_SIZE_MIN` is 1024, and `DP_METER_NUM_MAX` is 200000. `struct dp_meter_band` stores band type, rate, burst size, current bucket, and stats. `struct dp_meter` stores a per-meter spinlock, RCU head, id, kbps and keep-stats flags, band count, maximum delta, last-used time, aggregate stats, and flexible bands. `struct dp_meter_instance` is an RCU-freeable flexible array of meter pointers. `struct dp_meter_table` stores the current instance, count, and maximum allowed meters.

The public API is `ovs_meters_init()`, `ovs_meters_exit()`, and `ovs_meter_execute()`. `dp_meter_genl_family` is externally visible for datapath module generic-netlink registration.

## Control Flow and Integration
`datapath.c` embeds `struct dp_meter_table` in each datapath and registers `dp_meter_genl_family` with other OVS netlink families. `actions.c` calls `ovs_meter_execute()` for `OVS_ACTION_ATTR_METER`.

## State and Persistence
The structures hold volatile in-memory state. Locking is split between OVS mutex/RCU for table membership and per-meter spinlock for bucket and stats mutation.

## Dependencies
It depends on Open vSwitch UAPI types, skbuffs, bit helpers, module initialization headers, and `flow.h` for `struct sw_flow_key` and stats.

## Risks
Any change to limits, flexible-array layout, or locking rules must stay synchronized with `meter.c` and userspace feature replies. Callers must not free meters directly.

## Test Signals
Build coverage, meter generic-netlink tests, action execution tests, and lockdep under concurrent meter updates validate this header contract.
