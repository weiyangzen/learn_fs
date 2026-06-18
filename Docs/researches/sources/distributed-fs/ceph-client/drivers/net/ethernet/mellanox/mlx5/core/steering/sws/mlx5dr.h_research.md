# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/mlx5dr.h

## Purpose
This is the public software-steering direct-rule API header. It exposes opaque domain/table/matcher/rule/action types, lifecycle functions, action constructors, support checks, sync flags, reformat types, match parameter wrapper, destination wrapper, and buddy allocator APIs.

## Important APIs, Types, And Functions
Public domain and object APIs include `mlx5dr_domain_create/destroy/set_peer`, `mlx5dr_table_create/destroy/get_id/get_from_fs_ft/set_miss_action`, `mlx5dr_matcher_create/destroy`, `mlx5dr_rule_create/destroy`, and `mlx5dr_action_destroy`.

Action constructors cover destination table/table number/FW table/vport, multi-destination table, drop, tag, sampler, counter, packet reformat, modify header, pop/push VLAN, ASO, and match-range destination. `mlx5dr_action_get_pkt_reformat_id()` exposes reformat IDs. `mlx5dr_is_supported()` gates support on RoCE and SW-owner capabilities, with a steering-format limit for SW owner v2.

The buddy allocator API declares init/cleanup/alloc/free for ICM memory management.

## Control Flow
Consumers such as `fs_dr.c` create a domain, create tables and matchers, create actions, then create rules that bind values and actions. Destroy calls unwind in reverse. Support checking happens before selecting the DR command backend.

## State And Persistence
The header hides object internals behind forward declarations. Persistent state lives in the private `dr_types.h` structures and hardware resources allocated by the implementation. Match parameters are passed as device-spec buffers through `struct mlx5dr_match_parameters`.

## Dependencies And Integration Points
It is included by `fs_dr.h`, private DR modules, and generic flow steering code. It intentionally provides a smaller API than `dr_types.h`, keeping internals private except for the buddy allocator structure needed by ICM code.

## Risks
This is an API boundary: prototype or enum changes affect all callers. The inline `mlx5dr_is_supported()` depends on current device capability semantics; overly broad support would select SW steering on unsupported hardware, while overly narrow support would disable valid devices.

## Test Signals
Build tests for public callers, DR-enabled namespace creation through FS, support-check tests across capability combinations, and lifecycle tests for every public object/action constructor.
