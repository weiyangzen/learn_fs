# sources/distributed-fs/ceph-client/include/uapi/linux/net_shaper.h

## Purpose
Defines the auto-generated generic netlink ABI for network shapers: family metadata, shaper scope/metric enums, handle/capability attributes, and get/set/delete/group/capability commands.

## Important APIs, Types, And Functions
Exports `NET_SHAPER_FAMILY_NAME`, `NET_SHAPER_FAMILY_VERSION`, `net_shaper_scope`, `net_shaper_metric`, `NET_SHAPER_A_*`, handle attrs, capability attrs, and `NET_SHAPER_CMD_*`.

## Control Flow
Userspace queries capabilities, then gets/sets/deletes/groups shapers by handle. Scope determines whether handle ID is a netdevice, queue, or sched-tree node; metrics select BPS or PPS shaping.

## State, Persistence, And Dependencies
Shaper state persists in device or queue scheduling configuration. The header is generated from `net_shaper.yaml`.

## Integration Points
Used by YNL-aware tools, network drivers exposing hardware shapers, and traffic-management configuration.

## Risks
This ABI is generated and numeric IDs must remain stable. Capability attrs must be consulted before setting optional properties such as nesting, burst, priority, or weight.

## Test Signals
Validate family version, capability queries per ifindex/scope, set/get/delete round trips, nested group handling, unsupported metric rejection, and handle attr parsing.
