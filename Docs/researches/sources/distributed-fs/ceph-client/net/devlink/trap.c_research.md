# sources/distributed-fs/ceph-client/net/devlink/trap.c

## Purpose
This file implements devlink packet trap, trap group, and trap policer registration plus their generic netlink control and notification paths. It is the common devlink layer that lets switch/NIC drivers expose packets trapped to the CPU, configure drop-trap actions, associate trap groups with policers, report trap statistics, and feed drop monitor tracepoints.

## Important APIs, Types, And Functions
Internal objects wrap immutable driver-provided descriptors with runtime state:

- `struct devlink_trap_item`: descriptor, group pointer, mutable action, per-CPU stats, and driver private pointer.
- `struct devlink_trap_group_item`: descriptor, optional policer association, list node, and per-CPU group stats.
- `struct devlink_trap_policer_item`: descriptor plus mutable rate and burst.
- `struct devlink_stats`: per-CPU RX packet/byte counters protected by `u64_stats_sync`.

The exported registration API is `devl_traps_register()`, `devlink_traps_register()`, `devl_traps_unregister()`, `devlink_traps_unregister()`, `devl_trap_groups_register()`, `devlink_trap_groups_register()`, `devl_trap_groups_unregister()`, `devlink_trap_groups_unregister()`, `devl_trap_policers_register()`, and `devl_trap_policers_unregister()`. Runtime packet reporting is exported through `devlink_trap_report()`, and drivers recover their private cookie through `devlink_trap_ctx_priv()`.

Netlink handlers include `devlink_nl_trap_get_doit()`, `devlink_nl_trap_get_dumpit()`, `devlink_nl_trap_set_doit()`, group get/dump/set variants, and policer get/dump/set variants. Fill helpers serialize names, generic flags, action, type, metadata capabilities, stats, policer IDs, rate, and burst into devlink netlink attributes.

## Control Flow
Drivers register policers first if groups reference them, then groups, then traps. Verification distinguishes generic descriptors, whose IDs/names/types must match devlink's built-in tables, from driver-specific descriptors, whose IDs must sit outside the generic range and whose names must not collide with generic traps or groups.

Trap registration allocates a `devlink_trap_item`, per-CPU stats, links it to its initial group by ID, invokes `devlink->ops->trap_init()`, adds it to `devlink->trap_list`, and sends a `DEVLINK_CMD_TRAP_NEW` notification if the devlink is registered and listeners exist. Unregistration disables traps to drop, waits for RCU grace with `synchronize_rcu()`, then removes items in reverse order and calls optional driver fini hooks.

Netlink get/dump paths look up list entries and serialize state. Set paths validate action values, call driver callbacks, update cached state, and report extack errors. Group action setting either uses a driver group callback or falls back to per-trap action setting; group policer changes validate the policer ID and call `trap_group_set()`. Policer set validates rate/burst against min/max before calling `trap_policer_set()` and updating cached values.

When a driver reports a packet, `devlink_trap_report()` updates per-trap and per-group stats on the current CPU and emits the `devlink_trap_report` tracepoint with metadata derived from the trap item, group, input devlink port, and optional flow-action cookie.

## State And Persistence
All state is in memory under the owning `struct devlink`: `trap_list`, `trap_group_list`, and `trap_policer_list`. Mutable action, policer attachment, rate, burst, and counters persist only for the lifetime of the devlink instance and registered objects. Per-CPU stats are monotonically accumulated until unregistration frees them.

## Dependencies And Integration Points
The file depends on `devl_internal.h`, generic netlink devlink helpers, `trace/events/devlink.h`, `netdev_alloc_pcpu_stats()`, `u64_stats`, RCU synchronization, and driver callbacks in `struct devlink_ops`: trap init/fini/action, group init/set/action, policer init/fini/set/counter, and drop counters. Userspace integration is through devlink generic netlink commands and asynchronous notifications.

## Risks And Edge Cases
Group action setting may partially commit changes when per-trap fallback succeeds for earlier traps and later traps fail; the extack text explicitly warns about committed changes. Non-drop traps silently skip action changes when their current action differs, because only drop traps are action-mutable. Registration ordering matters: traps require groups to exist, and groups may require policers to exist. Statistics reads aggregate all possible CPUs and can be stale relative to concurrent reports, though `u64_stats_sync` avoids torn 64-bit values.

## Test Signals
Useful tests are devlink selftests or driver tests that register generic and driver traps, verify duplicate/name/ID rejection, perform netlink get/dump/set operations, change group actions and policers, check extack messages for invalid inputs, report packets, and validate per-trap/group counters plus drop monitor tracepoint emission.
