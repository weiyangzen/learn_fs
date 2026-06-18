# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/sws/fs_dr.c

## Purpose
This file adapts the generic mlx5 flow steering command interface to the software-steering direct-rule backend. It implements a `struct mlx5_flow_cmds` table whose operations create DR domains, tables, matchers, rules, packet reformats, modify headers, and peer relationships while delegating firmware-terminal tables back to the firmware command backend.

## Important APIs, Types, And Functions
The exported functions are `mlx5_fs_cmd_get_dr_cmds()`, `mlx5_fs_dr_is_supported()`, and `mlx5_fs_dr_action_get_pkt_reformat_id()`. The static command methods implement namespace create/destroy, table create/destroy/modify, group create/destroy, FTE create/update/delete, packet reformat alloc/free, modify header alloc/free, peer setup, root FT update, and capability reporting.

`mlx5_cmd_dr_create_fte()` is the main translation function. It converts a flow steering `fs_fte` into ordered `mlx5dr_action` arrays, creates terminal destination actions, handles special multi-destination tables, creates counters/tags/ASO actions, and calls `mlx5dr_rule_create()`.

## Control Flow
Table/group creation maps flow tables to `mlx5dr_table_create()` and groups to `mlx5dr_matcher_create()`. Rule creation builds ordered actions because SW steering supports constrained action ordering: decap/pop/modify on RX and modify/push/encap on TX. Packet reformat can be delayed so encapsulation happens after VLAN push/modify ordering. Terminal destinations are accumulated separately, then appended directly when single or wrapped in a multi-destination table action when multiple.

Update FTE creates a replacement rule first, then deletes the old rule. Delete FTE destroys the DR rule and then frees fs_dr-owned actions in reverse order. Table miss-action changes create a destination-table action for the next table and install it through `mlx5dr_table_set_miss_action()`.

## State And Persistence
DR-owned pointers are stored inside existing FS objects: namespace `fs_dr_domain`, flow table `fs_dr_table`, group `fs_dr_matcher`, FTE `fs_dr_rule`, packet reformat `fs_dr_action`, and modify header `fs_dr_action`. The adapter tracks only actions it created itself in `mlx5_fs_dr_rule.dr_actions`, so externally allocated packet reformat and modify header actions remain owned by their resource objects.

## Dependencies And Integration Points
It depends on flow steering core types, firmware command backend helpers, `mlx5dr.h` public APIs, `fs_dr.h` wrapper structs, and private `dr_types.h` for error logging and action internals. It is selected by `fs_core.c` when DR support is available and falls back to firmware commands for terminal tables and unsupported operations.

## Risks
Ownership is subtle: some actions are per-rule temporary and must be destroyed on failure/delete, while packet reformat and modify-header actions are resource-owned and must not be destroyed by rule cleanup. The hard action limit is 34, sized for 32 destinations plus extras. The function mutates `fte->act_dests.action.action` to drop packet reformat when a vport destination embeds a reformat ID. Update creates new then deletes old, so duplicate-rule or resource pressure behavior matters.

## Test Signals
Tests should cover rule creation failures at each allocation point, mixed action ordering, single and multi-destination rules, FW-owned reformat rejection, vport reformat handling, counters, flow tags, ASO flow meter, range destination, table miss chaining, update rollback, delete cleanup, terminal-table fallback, and capability bits for VLAN push/pop and match ranges.
