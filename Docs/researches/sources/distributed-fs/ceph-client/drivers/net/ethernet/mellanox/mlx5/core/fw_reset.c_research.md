# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.c

## Purpose
`fw_reset.c` implements mlx5 firmware reset negotiation and event handling. It supports devlink-controlled remote reset policy, live patch notifications, PCI sync reset request/ack/nack/unload/now/abort flows, reset timeout handling, PCI link toggle or hot reset, and reset completion/reload.

## Important APIs, Types, And Functions
- `struct mlx5_fw_reset` holds the device, EQ notifier, workqueue, work items, timeout work, flags, reset method, poll timer, completion, and result.
- Public APIs include `mlx5_fw_reset_query`, `mlx5_fw_reset_set_reset_sync`, `mlx5_fw_reset_set_live_patch`, `mlx5_fw_reset_in_progress`, `mlx5_fw_reset_wait_reset_done`, `mlx5_sync_reset_unload_flow`, `mlx5_fw_reset_verify_fw_complete`, event start/stop/drain, init, and cleanup.
- MFRL helpers query and set reset level/type/state/method plus sync start/ack/nack.
- Event workers handle live patch, reset request, unload, reload, reset-now, abort, and timeout.

## Control Flow And State
Initialization is gated by MFRL support, allocates state, creates a single-thread workqueue, registers the `ENABLE_REMOTE_DEV_RESET` devlink param, and initializes work items. Event start registers a general-event notifier. Firmware events dispatch either live-patch work or PCI sync reset state work.

For sync reset, an initiating devlink path calls `mlx5_fw_reset_set_reset_sync`, sets `PENDING_COMP`, and asks firmware to start PCI sync. External reset request events evaluate reset method, hotplug constraints, SF state, management-interface device IDs, and remote-reset policy before sending ACK or NACK. ACK starts health-poll suppression, sync-reset polling, timeout work, and marks reset in progress. Reset-now and unload flows run fast teardown and PCI reset/unload handling, then complete reload or completion.

## State And Persistence Behavior
State is entirely in `dev->priv.fw_reset`, flag bits, timer/workqueue state, MFRL firmware state, NIC interface reset state, and devlink runtime param. Cleanup unregisters the devlink param, drains work if requested, and destroys the workqueue. No filesystem persistence is used.

## Dependencies And Integration Points
The file depends on devlink, EQ notifiers, PCI config/reset APIs, mlx5 health polling, firmware tracer reload, SF table checks, HCA teardown from `fw.c`, device load/unload helpers, and timeout definitions. It coordinates with health recovery by stopping/restarting health polling around sync reset.

## Risks And Edge Cases
Incorrect flag transitions can leave health polling stopped, completion pending, or reset marked in progress. PCI link toggle must save/restore sibling device state and avoid hotplug-interrupt configurations. Reset requests can arrive during devlink reload, device removal, or mode changes. `mlx5_sync_reset_unload_flow` must correctly acknowledge drop mode and timeout if firmware never requests reset action.

## Test Signals
Cover MFRL unsupported init, devlink remote-reset enable/disable, sync reset ACK/NACK paths, reset timeout, abort, unload and reset-now events, live patch tracer reload, PCI hot reset/link toggle success and failure, reload-required handling, and no queued work after drain/cleanup.
