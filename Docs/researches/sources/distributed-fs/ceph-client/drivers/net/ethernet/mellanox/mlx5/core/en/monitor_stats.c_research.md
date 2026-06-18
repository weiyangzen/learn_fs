# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/en/monitor_stats.c

Purpose: configures mlx5 firmware monitor counters and handles monitor-counter EQ events by refreshing driver stats and rearming the counters.

Important APIs/functions: `mlx5e_monitor_counter_supported`, `mlx5e_monitor_counter_init`, and `mlx5e_monitor_counter_cleanup`. Internal helpers check capabilities, program PPCNT/Q-counter watch lists, arm counters, and process events through a work item.

Control flow: support detection checks every device in the scalable-device set for enough monitor counter capacity. Init installs a monitor-counter notifier per device, programs required PPCNT and rx-out-of-buffer q-counter monitors, arms each device, and queues stats update work. When an event arrives, a work item takes `state_lock`, updates NDO stats, releases the lock, and rearms all devices. Cleanup clears the monitor list in firmware, unregisters notifiers, and cancels work.

State and persistence: notifier and work structures live in `mlx5e_priv`; firmware monitor counter configuration persists until cleanup or device reset.

Dependencies and integration: uses mlx5 EQ notifiers, command opcodes `SET_MONITOR_COUNTER` and `ARM_MONITOR_COUNTER`, scalable-device iteration, q-counter ids, and mlx5e stats update.

Risks: command execution errors are ignored in setup/arm paths, so lack of monitor functionality may be silent after support checks. Event storms depend on workqueue serialization and rearm behavior.

Test signals: devices with and without PPCNT/Q-counter capacities, SD multi-device setups, EQ event handling, cleanup ordering, and stats refresh after rx-out-of-buffer events.
