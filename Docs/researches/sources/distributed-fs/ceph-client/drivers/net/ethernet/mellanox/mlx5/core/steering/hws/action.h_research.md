# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/steering/hws/action.h

## Purpose
`action.h` is the internal Hardware Steering action contract for mlx5 HWS. It defines how higher-level rule actions are represented as steering table context (STC) slots, WQE data words, action templates, and concrete action objects. It is consumed by rule insertion, BWC compatibility code, action STE pools, command wrappers, debug dumping, and matcher setup.

## Important APIs, Types, And Functions
Key constants describe the action STE budget (`MLX5HWS_ACTION_MAX_STE`), STC indexes, action data offsets, and header/reformat sizes. `struct mlx5hws_action_default_stc` and `struct mlx5hws_action_shared_stc` are context-owned reusable STC resources with refcounts protected by `ctx->ctrl_lock`. `struct mlx5hws_actions_apply_data` is the transient rule-WQE population state, and `struct mlx5hws_actions_wqe_setter` stores per-stage callbacks plus slot indexes. `struct mlx5hws_action_template` is the processed sequence used by matchers, while `struct mlx5hws_action` stores action-specific backing objects such as STCs, modify-header pattern/argument IDs, packet reformat IDs, destination arrays, ASO objects, range tables, and table jumps.

The exported helpers include action type formatting, default STC get/put, decap L3 data preparation, action-template processing, combination validation, and single STC allocation/free. The inline setters fill missing action slots with default NOP STCs and `mlx5hws_action_apply_setter()` writes the control, action, and hit STC indexes into the WQE.

## Control Flow And State
Action template processing precomputes setter callbacks and flags; rule creation later iterates setters and calls `mlx5hws_action_apply_setter()`. The inline path always emits a control STC, handles either normal single/double/triple action layouts or jumbo STE layout, then emits the hit action and encodes the number of STC actions in the control STC index word.

## Dependencies And Integration Points
This header depends on HWS context, pools, command STC attributes, send queues, rule actions, and mlx5 PRM action types supplied through `internal.h`. BWC uses action templates for compatibility matchers, action STE pool code allocates jump-to-STE-table STCs with these offsets, and debug code prints action-template contents through `mlx5hws_action_type_to_str()`.

## Risks And Test Signals
The main risks are STC index/offset mismatches, incorrect action-combination classification, refcount imbalance for shared/default STCs, and endian mistakes while writing WQE data. Useful test signals are rule insertion with no-op/default slots, combinations of single/double/triple actions, jumbo STE rules, decap/reformat actions, and teardown paths that verify shared STC reference counts return to zero.
