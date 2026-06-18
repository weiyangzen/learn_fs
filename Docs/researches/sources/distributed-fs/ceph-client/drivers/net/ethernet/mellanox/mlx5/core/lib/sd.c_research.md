# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.c

## Purpose
`sd.c` implements mlx5 Socket-Direct multi-PF grouping. It discovers devices that firmware marks as one Socket-Direct group, elects a primary PF, disconnects secondary PFs from direct network steering, creates alias access from secondaries to the primary TX flow table, exposes debugfs group details, and redirects auxiliary-device access from secondaries to primary devices when needed.

## Important APIs, types, and functions
Public APIs are `mlx5_sd_init()`, `mlx5_sd_cleanup()`, channel-index helpers, peer lookup, and auxiliary-device get/put helpers. `struct mlx5_sd` stores group ID, host bus count, devcom component, debugfs dentry, up/down state, primary flag, and a union of primary or secondary fields. Internal helpers query MPIR/NIC vport SD group, test capability support, register with devcom, set/unset primary and secondary hardware state, create/destroy alias flow tables, and print/debug group members.

## Control flow
Initialization first filters to non-embedded PFs, reads SD group metadata, checks capability support, allocates `struct mlx5_sd`, and registers a devcom component keyed by group ID and network namespace. Once the devcom component size equals `host_buses`, the group is marked ready, the lowest PCI bus is elected primary, and peer pointers are filled. The first device that observes a ready down group creates a primary egress flow table, grants other-vHCA access with a random key, creates alias objects on secondaries, sets secondary TX root to the alias object, enables silent L2 mode on secondaries, creates debugfs files, and marks the group up. Cleanup reverses this sequence under the devcom component lock and clears peer pointers before unregistering.

## State and persistence behavior
State is volatile: `dev->sd`, devcom membership, flow table aliases, silent-mode settings, TX root steering, debugfs entries, and device references. Hardware state is restored during cleanup by resetting TX roots, destroying aliases, destroying the primary flow table, and disabling silent mode.

## Dependencies and integration points
The file depends on devcom grouping, flow steering commands, vport SD group query, MPIR register query, debugfs, random key generation, auxiliary devices, and mlx5 alias-object commands declared in `mlx5_core.h`. It is initialized during core once-only setup and affects channel mapping, auxiliary-device routing, and multi-PF netdev composition.

## Risks and edge cases
Group bring-up is sensitive to lock ordering and partial failure rollback. The code documents auxiliary-device lock ordering to avoid ABBA. Only groups up to `MLX5_SD_MAX_GROUP_SZ` are supported. Capability mismatch skips combining rather than failing probe. A secondary removal while an auxiliary device is being redirected requires the recheck after dropping devcom lock and taking `device_lock()`.

## Test signals
Test two-PF Socket-Direct systems, unsupported capability skip, primary election by PCI bus number, devcom readiness when all peers register, cleanup on removal of primary or secondary, debugfs contents, alias-object failure rollback, silent-mode restoration, channel-index mapping, and auxiliary-device redirect races during remove.
