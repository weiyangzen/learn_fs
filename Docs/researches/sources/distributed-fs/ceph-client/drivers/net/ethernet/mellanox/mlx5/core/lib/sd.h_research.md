# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/lib/sd.h

## Purpose
`sd.h` declares the mlx5 Socket-Direct public helper API and iteration macros used by core and Ethernet code to address devices within a combined multi-PF group.

## Important APIs, types, and functions
It defines `MLX5_SD_MAX_GROUP_SZ` as 2 and forward-declares `struct mlx5_sd`. Public helpers include primary peer lookup, channel-index-to-device/vector mapping, channel-index-to-device lookup, auxiliary-device get/put redirection, and init/cleanup. Iteration macros cover all group devices, all devices up to a target, secondaries only, and secondaries up to a target.

## Control flow
The header has no standalone runtime flow. Its macros repeatedly call `mlx5_sd_primary_get_peer()` and stop when no peer or a specified target is reached. Callers use these macros to apply setup/teardown across primary and secondary devices in group order.

## State and persistence behavior
No state is stored in the header. It defines group-size and iteration semantics over state owned by `sd.c` and stored in `dev->sd`.

## Dependencies and integration points
It integrates Socket-Direct support with channel allocation, auxiliary-device routing, and core setup/cleanup. It assumes `struct mlx5_core_dev` and `struct auxiliary_device` are visible to includers.

## Risks and edge cases
The maximum group size is a software limit; firmware groups larger than two are intentionally unsupported. Iteration macros evaluate peer lookup each loop and rely on stable group state under the caller's locking.

## Test signals
Build coverage plus Socket-Direct runtime tests through `sd.c` validate the header. Unit-style checks can verify channel index modulo/division mapping and macro iteration boundaries.
