# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/mlx5hws.h

## Purpose
`mlx5hws.h` is the public in-kernel API for mlx5 Hardware Steering. It defines opaque context/table/matcher/rule handles, table and matcher attributes, action types and flags, rule attributes, per-action payload structures, queue operations, debug dumping, and BWC helper APIs used by the flow-steering adapter.

## Important APIs, types, and functions
The header defines table type `MLX5HWS_TABLE_TYPE_FDB`, matcher resource modes, action types for drop, miss, table, counter, tag, modify header, vport, VLAN, reformat, ASO meter, insert/remove header, range, sampler, destination arrays, and `LAST`. It also defines action flags, ASO meter colors, send queue drain flags, context/table/matcher/rule attributes, and `struct mlx5hws_rule_action` payloads for tag, counter, modify header, reformat, push VLAN, and ASO meter.

Public lifecycle APIs include `mlx5hws_context_open()`, `mlx5hws_context_close()`, `mlx5hws_context_set_peer()`, table create/destroy/get-id/default-miss functions, match/action template create/destroy functions, matcher create/destroy/attach/resize functions, rule create/destroy/update functions, action create/destroy/get-type/get-dev functions, send queue poll/action, and debug dump. The BWC section declares blocking matcher and rule helpers used by `fs_hws.c`.

## Control flow
This header has no executable flow except `mlx5hws_is_supported()`, which checks device capabilities for WQE-based flow-table updates and ignoring flow-level RTC validity. Normal callers open a context, create tables, create match and action templates, create matchers, create actions, enqueue rules on send queues, drain or poll completions, update/destroy rules, then destroy objects in reverse order. BWC callers use simplified blocking matcher/rule operations that internally create templates, attach action templates as needed, and poll to completion.

## State and persistence behavior
Opaque objects represent HWS firmware resources and driver state. Contexts own queues, protection domain data, caps, caches, and common resources. Tables own flow-table IDs and default miss state. Matchers own definers, RTCs, STE ranges, and action template state. Actions own STC/action resources and sometimes argument or pattern objects. Rule handles track hardware insertion state and are asynchronous unless BWC helpers are used.

## Dependencies and integration points
The API depends on mlx5 core devices, flow tables, rule attributes, PRM action data, send queues, and firmware object commands implemented in private HWS modules. Its main in-tree consumer in this subset is `fs_hws.c`, which maps generic flow steering to the BWC API and shared action constructors.

## Risks and edge cases
The API exposes both asynchronous rule operations and blocking BWC helpers; callers must honor queue IDs, user-data completion requirements, action ordering, and object lifetime. Action offsets point into shared argument resources and are not atomically reusable. Matcher insert/distribute modes are capability-dependent. FDB tables have mirrored RX/TX resources and flow-source optimization, so callers must set attributes consistently.

## Test signals
Build coverage of all declarations, HWS support gating on devices with and without required caps, context/table/matcher/action/rule lifecycle tests, queue drain and poll tests, BWC rule create/update/destroy, all action constructors used by flow steering, matcher resize and rule move, and debug dump coverage.
