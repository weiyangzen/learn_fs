# sources/distributed-fs/ceph-client/drivers/net/ethernet/mellanox/mlx5/core/devlink.c

## Purpose

`devlink.c` implements the core mlx5 devlink operations and driver-init parameters. It exposes firmware flashing, device info, firmware activation reloads, traps, Ethernet/RDMA/vDPA enablement, EQ sizing, hairpin sizing, max MAC list sizing, PCIe congestion thresholds, and vendor NV params.

## Important APIs, Types, and Functions

- `mlx5_devlink_alloc()` / `mlx5_devlink_free()` allocate the core devlink with `mlx5_devlink_ops`.
- `mlx5_devlink_flash_update()` calls `mlx5_firmware_flash()`.
- `mlx5_devlink_info_get()` reports board serials from VPD, PSID, running firmware version, and stored firmware version.
- `mlx5_devlink_reload_down()` and `mlx5_devlink_reload_up()` implement `driver_reinit` and `fw_activate`, including live patch for `DEVLINK_RELOAD_LIMIT_NO_RESET`.
- Trap helpers include `mlx5_devlink_traps_register()`, `mlx5_devlink_trap_report()`, `mlx5_devlink_trap_action_set()`, and action lookup/count helpers.
- `mlx5_devlink_params_register()` registers base, auxdev, max-MAC, PCIe congestion, and NV params; unregister reverses that order.
- Validation helpers enforce RoCE support, EQ depth range, hairpin queue constraints, num-doorbells limits, max MAC power-of-two constraints, and PCIe congestion threshold ranges.

## Control Flow

Devlink registration starts by registering static driver-init params and setting defaults from current device capabilities. Optional auxdev params are registered only if the matching feature is supported. Error handling unwinds previously registered param groups in reverse order.

Reload down rejects firmware reset in progress, multiport slaves, unsupported firmware activation, and non-driver-reinit operations on lightweight devices. Driver reinit unloads the device; firmware activation either triggers live patch or requests synchronized firmware reset and unload flow. Reload up reloads the driver and verifies firmware reset completion for full firmware activation.

Trap registration creates one list entry per trap in `dev->priv.traps`. Action changes are rejected in switchdev mode, limited to DROP/TRAP, and propagated through the mlx5 blocking notifier chain so consumers can veto by returning `NOTIFY_BAD`.

## State and Persistence Behavior

Persistent state includes devlink registered params and driver-init values, trap list entries under `dev->priv.traps`, firmware activation/reload side effects, and devlink info exposed to userspace. Driver-init params are intended to take effect on reload/rescan rather than immediately changing active datapath state.

## Dependencies and Integration Points

The file integrates with firmware flashing/reset (`fw_reset.h`), mlx5 health reset flows, eswitch devlink operations and rate objects, SF management, NV params, Ethernet/RDMA/vDPA auxiliary-device gating, LAG/multiport checks, and Linux devlink trap/param/info/reload APIs.

## Risks and Edge Cases

- `mlx5_devlink_serial_numbers_put()` suppresses VPD allocation failures by returning success, so missing serials are not fatal.
- Reload with VFs present is only warned as unfavorable, not blocked.
- Firmware live patch requires reset-level 0 support; full activate requires reset-level 3. Wrong expectations produce explicit extack errors.
- Trap action changes rely on notifier consumers to program hardware and report errors in `trap_event_ctx.err`.
- Param defaults are computed from current capabilities; after firmware change, callers must ensure values are reconciled with new caps.

## Test Signals

Use `devlink dev info`, firmware flash dry/error paths, `devlink dev reload action driver_reinit`, full `fw_activate`, and `limit no_reset` live patch. Validate param registration across PF/VF/SF/lightweight devices and unsupported capability cases. Test trap registration/action/reporting in legacy and switchdev modes. Fault-inject param registration failures to verify unwind order.
