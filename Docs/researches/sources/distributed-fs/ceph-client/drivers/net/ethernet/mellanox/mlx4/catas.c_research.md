# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx4/catas.c

## Purpose
This file implements mlx4 catastrophic/internal error detection and recovery. It polls firmware error state, detects PF/VF communication-channel internal errors, captures crash dumps for PFs, resets the device or asks the PF to reset a VF, and notifies clients.

## Important APIs and Functions
- `mlx4_start_catas_poll()` maps the PF catastrophic error buffer and starts a timer.
- `poll_catas()` detects slave comm-channel internal errors, PF catas buffer nonzero state, or persistent internal-error marks.
- `mlx4_enter_error_state()` performs reset handling and dispatches `MLX4_DEV_EVENT_CATASTROPHIC_ERROR`.
- `mlx4_reset_master()` and `mlx4_reset_slave()` implement PF and VF reset flows.
- `mlx4_catas_init()`/`mlx4_catas_end()` manage the single-thread health workqueue.

## Control Flow
The timer periodically polls. On error it queues `catas_work`, which calls `mlx4_handle_error_state()`. The handler enters error state, resets hardware, wakes pending command completions, dispatches events, and if interfaces are up attempts `mlx4_restart_one()` under devlink and interface-state locking.

## State and Persistence
Persistent device state is held in `dev->persist->state`, `interface_state`, workqueue/work item, and the mapped `priv->catas_err.map`. Module parameter `internal_err_reset` controls whether reset flow is active.

## Dependencies and Integration Points
It integrates with PCI config access, mlx4 reset/restart, devlink locking, command completion wakeups, crash dump collection, event dispatch, timers, and workqueues.

## Risks and Test Signals
Risks include reset while PCI channel is offline, BUG_ON on unrecoverable reset failure, race with device deletion, and missed health-buffer mapping. Test signals include injected firmware health errors, VF reset request/ack toggles, PCI EEH/offline paths, devlink restart logs, and client catastrophic event reception.
