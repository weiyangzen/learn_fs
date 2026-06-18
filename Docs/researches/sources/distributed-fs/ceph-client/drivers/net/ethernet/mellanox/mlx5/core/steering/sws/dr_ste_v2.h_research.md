# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/dr_ste_v2.h

## Purpose
This header defines the v2 modify-header hardware field codes and the mapping from software `MLX5_ACTION_IN_FIELD_*` selectors to those codes, bit starts/ends, and L3/L4 type restrictions.

## Important APIs, Types, And Functions
The central artifact is `dr_ste_v2_action_modify_field_arr[]`, a `static const struct mlx5dr_ste_action_modify_field` indexed by `MLX5_ACTION_IN_FIELD_*`. It covers L2 source/destination MAC, ethertype, DSCP, TCP/UDP ports, TCP flags, TTL/hop limit, IPv4/IPv6 addresses, metadata registers A/B/C, TCP sequence/ack, first VLAN ID, and EMD fields.

## Control Flow
There is no executable control flow. `dr_ste_v2.c` installs this array into `ste_ctx_v2`, and generic modify-header conversion code indexes it when compiling user-requested set/add/copy operations.

## State And Persistence
No runtime state is stored. The array is read-only driver data that must match the v2 hardware steering format.

## Dependencies And Integration Points
The array type comes from `dr_types.h` through the include chain in users. It is consumed by `dr_ste_v2.c` and v3 also reuses this array for modify-header field conversion.

## Risks
The v2 register C field codes differ from v1; copy/paste mistakes here would specifically break metadata register modifications. Because this is a header with a `static const` array, every including C file gets its own internal copy, which is intentional but worth remembering for size and linkage.

## Test Signals
Tests should exercise all supported modify-header fields, especially metadata register C0-C5 and EMD fields. Compile tests should catch missing enum definitions from include-chain changes.
