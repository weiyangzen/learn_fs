# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/sf/vhca_event.c

## Purpose

`sf/vhca_event.c` provides VHCA state event infrastructure for mlx5 SF management. It enables VHCA state event capabilities, creates per-bucket workqueues, handles EQ state-change events, queries full state from firmware, rearms events, traces them, and fans them out to blocking notifier subscribers.

## Important APIs, Types, and Functions

Private types are `struct mlx5_vhca_event_work`, carrying a function id event into process context, `struct mlx5_vhca_event_handler`, owning one workqueue, and `struct mlx5_vhca_events`, grouping `MLX5_DEV_MAX_WQS` handlers. Public functions include `mlx5_cmd_query_vhca_state()`, `mlx5_modify_vhca_sw_id()`, `mlx5_vhca_event_arm()`, `mlx5_vhca_state_cap_handle()`, `mlx5_vhca_state_notifier_init()`, `mlx5_vhca_event_init()`, `mlx5_vhca_event_cleanup()`, `mlx5_vhca_event_start()`, `mlx5_vhca_event_stop()`, `mlx5_vhca_event_notifier_register()`, `mlx5_vhca_event_notifier_unregister()`, `mlx5_vhca_events_work_enqueue()`, and `mlx5_vhca_event_work_queues_flush()`.

## Control Flow

Initialization sets up a blocking notifier head and an EQ notifier for `VHCA_STATE_CHANGE`, then `mlx5_vhca_event_init()` allocates a `vhca_events` object and creates multiple single-threaded workqueues. Start registers the EQ notifier. When an EQ event arrives, `mlx5_vhca_state_change_notifier()` allocates a work item with `GFP_ATOMIC`, records the function id, chooses a workqueue by function id modulo `MLX5_DEV_MAX_WQS`, and queues it.

The work handler calls `mlx5_vhca_event_notify()`, which queries the current VHCA state and software function id, rearms change events for that function, emits `mlx5_sf_vhca_event`, and calls every blocking notifier in `dev->priv.vhca_state_n_head`. Stop unregisters the EQ notifier and flushes all workqueues so no pending events race with cleanup.

## State and Persistence Behavior

Driver state includes `dev->priv.vhca_events`, `vhca_state_nb`, and `vhca_state_n_head`. Firmware state includes VHCA event capability bits, per-function `arm_change_event`, `sw_function_id`, and current state. Event work is transient and freed after notification.

## Dependencies and Integration Points

The file depends on command layouts from `mlx5_ifc_vhca_event.h`, EQ notifier infrastructure, workqueues, SF tracepoints, and capability macros. Subscribers include SF devlink state tracking, SF hardware-table deferred free, and SF auxiliary device discovery.

## Risks and Edge Cases

The EQ event carries only function id; the work item queries firmware later, so rapid state transitions may collapse into the latest state. If rearming fails, the code still notifies subscribers but future events may be missed. Workqueue allocation failure drops events. Stop must flush after unregistering to prevent callbacks into freed SF tables.

## Test Signals

Test capability enable bits in `set_hca_cap`, active/in-use/teardown/allocated transitions, event rearm after every event, notifier registration/unregistration order, workqueue flush on unload, dropped-work allocation fault injection, and tracepoint correlation with devlink SF state.
