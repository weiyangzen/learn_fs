# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/fw_reset.h

## Purpose
`fw_reset.h` declares the firmware reset interface shared between mlx5 core, devlink reload paths, health recovery, and event setup/teardown.

## Important APIs, Types, And Functions
- Query/control: `mlx5_fw_reset_query`, `mlx5_fw_reset_set_reset_sync`, `mlx5_fw_reset_set_live_patch`, and `mlx5_fw_reset_in_progress`.
- Completion/reload: `mlx5_fw_reset_wait_reset_done`, `mlx5_sync_reset_unload_flow`, and `mlx5_fw_reset_verify_fw_complete`.
- Event lifecycle: `mlx5_fw_reset_events_start`, `mlx5_fw_reset_events_stop`, and `mlx5_drain_fw_reset`.
- Allocation lifecycle: `mlx5_fw_reset_init` and `mlx5_fw_reset_cleanup`.

## Control Flow And State
The header exposes a lifecycle where device initialization creates reset state, event setup registers firmware event handling, devlink or firmware events initiate reset operations, wait/verify APIs synchronize with completion, drain stops pending work during removal, and cleanup frees state.

## Dependencies And Integration Points
It includes `mlx5_core.h` for core device and devlink extension-ack types. Consumers include core device load/unload, devlink reload, firmware flashing activation, and health/error paths that must know whether a firmware reset is active.

## Risks And Edge Cases
Callers must handle the no-op case where firmware reset support is absent and `dev->priv.fw_reset` is null. Wait/verify APIs are meaningful only after a reset has been initiated. Event start/stop should remain paired with device event-notifier lifecycle.

## Test Signals
Build coverage across configurations and runtime tests for init returning 0 on unsupported firmware, null-safe event start/stop/drain, and successful reset wait/verify sequencing after devlink firmware activation.
