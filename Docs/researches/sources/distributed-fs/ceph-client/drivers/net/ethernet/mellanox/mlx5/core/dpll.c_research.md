# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/dpll.c

## Purpose

`dpll.c` is the mlx5 auxiliary DPLL driver for SyncE/EEC support. It registers a Linux DPLL device and input pin, maps mlx5 SyncE firmware status into DPLL lock/pin/quality-level state, tracks the uplink netdev for pin association, and periodically notifies userspace when lock or pin state changes.

## Important APIs, Types, and Functions

- `struct mlx5_dpll` stores DPLL device/pin handles, trackers, mlx5 core device, workqueue, last-notified status, notifier block, and tracked netdev.
- Firmware register helpers: `mlx5_dpll_clock_id_get()`, `mlx5_dpll_synce_status_get()`, and `mlx5_dpll_synce_status_set()`.
- Mapping helpers convert firmware status to `enum dpll_lock_status`, lock-status error, pin state, fractional frequency offset, and ITU option 1 quality levels.
- DPLL ops: `mlx5_dpll_device_lock_status_get()`, `mlx5_dpll_device_mode_get()`, `mlx5_dpll_clock_quality_level_get()`.
- Pin ops: direction get, state get/set, and FFO get.
- `mlx5_dpll_probe()` creates/registers the DPLL device and pin, creates a workqueue, tracks netdev events, and starts periodic polling.
- `mlx5_dpll_remove()` cancels polling, unregisters tracking, destroys DPLL objects, and returns firmware to free-running.

## Control Flow

Probe first sets SyncE admin state to free-running, reads a clock identity, allocates state, gets shared DPLL/pin objects by clock ID and device index, registers them with callbacks, creates a single-thread workqueue, registers a blocking notifier for uplink netdev events, replays the current uplink event, and queues periodic work.

Periodic work reads `MSEES`, derives lock and pin state, sends DPLL change notifications when the value differs from the last valid sample, records the new values, and reschedules itself every 500 ms. Pin state set writes `MSEES` to switch firmware between track and free-running.

## State and Persistence Behavior

Persistent state includes the auxiliary driver's `mlx5_dpll`, registered DPLL device/pin references, firmware SyncE admin status, last observed lock/pin state, workqueue/delayed work, and netdev pin association. Firmware SyncE state is explicitly reset to free-running at probe start and remove end.

## Dependencies and Integration Points

Depends on Linux DPLL subsystem, auxiliary bus, mlx5 register access (`MSECQ`, `MSEES`), mlx5 blocking notifier events, uplink netdev replay, and `CONFIG_MLX5_DPLL` aux-device creation in `dev.c`.

## Risks and Edge Cases

- Periodic register polling every 500 ms can keep reporting delayed state if firmware access fails; failures simply reschedule.
- Quality-level mapping currently accepts network option 1 only and returns `-EINVAL` for unknown codes.
- Multiple mlx5 devices may share a DPLL device and pin; tracker usage must stay paired.
- Remove cancels work before unregistering notifiers, which is important for avoiding callbacks after free.
- Suspend/resume are no-ops; platform power flows rely on upper mlx5 cleanup/reprobe behavior.

## Test Signals

Register the `mlx5_core.dpll` auxiliary driver on SyncE-capable hardware, inspect DPLL netlink state, toggle pin state, disconnect media, and verify lock/pin notifications. Test shared-clock multiport devices and module unload/reload. Fault-inject register access failures.
