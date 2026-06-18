# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.c

## Purpose

`steering/hws/action.c` is the mlx5 hardware steering action engine. It validates action ordering, creates and destroys action objects, allocates STC resources, builds shared/default STCs, creates backing firmware objects for destination arrays, samplers, ranges, reformat, and modify-header actions, and converts rule-time action data into WQE control/data setters.

## Important APIs, Types, and Functions

Public action creation APIs include `mlx5hws_action_create_dest_table_num()`, `mlx5hws_action_create_dest_table()`, `mlx5hws_action_create_dest_drop()`, `mlx5hws_action_create_default_miss()`, `mlx5hws_action_create_tag()`, `mlx5hws_action_create_aso_meter()`, `mlx5hws_action_create_counter()`, `mlx5hws_action_create_dest_vport()`, `mlx5hws_action_create_push_vlan()`, `mlx5hws_action_create_pop_vlan()`, `mlx5hws_action_create_reformat()`, `mlx5hws_action_create_modify_header()`, `mlx5hws_action_create_dest_array()`, `mlx5hws_action_create_insert_header()`, `mlx5hws_action_create_remove_header()`, `mlx5hws_action_create_dest_match_range()`, `mlx5hws_action_create_last()`, `mlx5hws_action_create_flow_sampler()`, and `mlx5hws_action_destroy()`.

Template APIs are `mlx5hws_action_template_create()`, `mlx5hws_action_template_process()`, and `mlx5hws_action_template_destroy()`. STC helper APIs used by other HWS files are `mlx5hws_action_alloc_single_stc()`, `mlx5hws_action_free_single_stc()`, `mlx5hws_action_get_default_stc()`, `mlx5hws_action_put_default_stc()`, `mlx5hws_action_prepare_decap_l3_data()`, `mlx5hws_action_type_to_str()`, `mlx5hws_action_get_type()`, and `mlx5hws_action_get_dev()`.

Key local helpers include `hws_action_fill_stc_attr()`, `hws_action_fixup_stc_attr()`, shared STC get/put functions, reformat and modify-header builders, range action table builders, WQE setter functions, and action order validation against `action_order_arr`.

## Control Flow

Action creation starts with generic allocation and validation. `hws_action_create_generic_bulk()` requires HWS FDB flags, checks context HWS support and eswitch-manager restrictions, allocates one or more `struct mlx5hws_action`, and initializes type/context/flags. `hws_action_create_stcs()` fills an STC attribute for the action type, locks `ctx->ctrl_lock`, and allocates an STC from `ctx->stc_pool`; FDB actions program both the base and mirror STC objects. `hws_action_fixup_stc_attr()` adapts STCs for table direction and mirror behavior, such as turning ignored mirror table jumps into DROP, converting ALLOW to JUMP_TO_VPORT in FDB TX/RX, turning uplink vport jumps into JUMP_TO_UPLINK, and suppressing TAG in FDB TX.

Simple actions allocate a single STC for drop, miss, tag, counter, ASO meter, table jump, vport jump, push/pop VLAN, remove header, and tunnel L2 decap. Pop VLAN also obtains a shared double-pop STC. Reformat actions are specialized: L2-to-tunnel uses header insert with an argument object; L2-to-tunnel-L3 combines a shared decap-L3 STC with insert; tunnel-L3-to-L2 builds a modify-header program that removes outer headers, inserts L2 bytes in reverse-order inline chunks, and removes padding. Modify-header actions calculate NOP insertion for hardware constraints, optionally allocate a shared argument object, use inline single actions when possible, otherwise allocate patterns and argument storage.

Destination arrays and samplers create intermediate firmware forwarding tables ("islands") with `mlx5hws_cmd_forward_tbl_create()` and then an STC pointing to that table. Range destination creates a definer on outer packet length, an STE pool, paired RTCs for FDB base/mirror, an always-hit match STE plus range STE through the control send queue, a hit table action, and an STC that jumps into the STE table.

Action template processing maps a validated action-type list into a sequence of WQE setter slots. It reserves one extra setter for jumbo/match STE jump-in, assigns counter, single, double, remove, insert, modify, ASO, and hit setters, handles two POP_VLAN actions through a shared double-pop STC, installs a default hit STC if no terminal hit action is supplied, computes the number of action STEs, and marks templates that only terminate without action DWs.

## State and Persistence Behavior

Persistent HWS state includes allocated action objects, STC pool chunks, default and shared STCs in `ctx->common_res`, argument objects, pattern ids, packet reformat objects, forwarding tables, range definers, STE pools, RTC ids, and action templates. Most firmware resource programming happens under `ctx->ctrl_lock` because modifying shared STC bases in parallel is unsupported. Rule-time WQE setters may write non-shared modify/reformat arguments into argument memory and set `apply->require_dep` so dependent writes are ordered.

## Dependencies and Integration Points

The file depends on nearly all HWS infrastructure: context capabilities, STC/RTC/forward-table command wrappers, STC and STE pools, pattern manager, argument manager, send queues, definers, table type translation, flow table objects, flow destination types, ASO meter constants, and public HWS action types from `mlx5hws.h`. It integrates with rule creation through action templates and setters, with FDB mirror tables, and with FS/HWS compatibility layers that create these actions for flow steering.

## Risks and Edge Cases

The action ordering array is the gatekeeper for supported sequences; new action types must update the order array, string table, STC fill, destroy, and template setter logic together. Bulk actions allocate arrays of `struct mlx5hws_action`; destroy paths assume the first action carries counts for all siblings. Shared actions reject combinations of shared flag, bulk size, and log bulk size that the implementation cannot represent. Error unwinds are complex, especially for range actions, destination arrays, and modify-header patterns/args. Several allocations occur under `ctx->ctrl_lock`; long command paths or send-queue drains can increase lock hold time. Runtime setters silently return if temporary allocation for NOP-expanded modify data fails, which can drop an argument write without direct rule-create failure.

## Test Signals

Test every public action type, valid and invalid action order combinations, FDB mirror behavior, merged and non-merged eswitch vport destinations, uplink destinations, shared/default STC refcounts, destroy after partial create failure, two-pop VLAN optimization, shared and non-shared reformat/modify-header actions, decap-L3 with and without VLAN, range destination packet-length matching, flow sampler and destination array forwarding tables, and rule-time WQE data writes. Fault injection should target STC allocation, command STC modify, pattern allocation, arg allocation/write, forwarding table create, RTC create, send-queue drain, and definer allocation.
